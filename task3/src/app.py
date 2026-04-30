"""Three caching strategies sharing the same get/set surface."""
import threading
import time
from queue import Queue, Empty

from .cache import Cache
from .db import DB


class CacheAside:
    """Lazy loading. Read: cache -> DB on miss -> populate cache. Write: DB only (cache invalidated)."""

    name = "cache_aside"

    def __init__(self, cache: Cache, db: DB) -> None:
        self.cache = cache
        self.db = db

    def get(self, key: str) -> str | None:
        v = self.cache.get(key)
        if v is not None:
            return v
        v = self.db.get(key)
        if v is not None:
            self.cache.set(key, v)
        return v

    def set(self, key: str, value: str) -> None:
        self.db.set(key, value)
        # write-around: drop stale cache entry so next read repopulates it
        self.cache.client.delete(key)

    def stop(self) -> None:
        pass

    def extra_stats(self) -> dict:
        return {}


class WriteThrough:
    """Read: cache -> DB on miss -> populate cache. Write: cache AND db synchronously."""

    name = "write_through"

    def __init__(self, cache: Cache, db: DB) -> None:
        self.cache = cache
        self.db = db

    def get(self, key: str) -> str | None:
        v = self.cache.get(key)
        if v is not None:
            return v
        v = self.db.get(key)
        if v is not None:
            self.cache.set(key, v)
        return v

    def set(self, key: str, value: str) -> None:
        self.cache.set(key, value)
        self.db.set(key, value)

    def stop(self) -> None:
        pass

    def extra_stats(self) -> dict:
        return {}


class WriteBack:
    """Read: cache -> DB on miss -> populate cache.
    Write: cache only; a background flusher drains dirty keys to DB in batches.
    """

    name = "write_back"

    def __init__(
        self,
        cache: Cache,
        db: DB,
        flush_interval: float = 0.5,
        batch_size: int = 200,
    ) -> None:
        self.cache = cache
        self.db = db
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self._dirty: Queue[tuple[str, str]] = Queue()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._max_queue = 0
        self._flush_batches = 0
        self._flush_rows = 0
        self._thread = threading.Thread(target=self._run, name="wb-flusher", daemon=True)
        self._thread.start()

    def get(self, key: str) -> str | None:
        v = self.cache.get(key)
        if v is not None:
            return v
        v = self.db.get(key)
        if v is not None:
            self.cache.set(key, v)
        return v

    def set(self, key: str, value: str) -> None:
        self.cache.set(key, value)
        self._dirty.put((key, value))
        qs = self._dirty.qsize()
        with self._lock:
            if qs > self._max_queue:
                self._max_queue = qs

    def _drain_batch(self) -> int:
        items: dict[str, str] = {}
        try:
            while len(items) < self.batch_size:
                k, v = self._dirty.get_nowait()
                items[k] = v  # last write wins in the batch
        except Empty:
            pass
        if not items:
            return 0
        self.db.set_many(list(items.items()))
        with self._lock:
            self._flush_batches += 1
            self._flush_rows += len(items)
        return len(items)

    def _run(self) -> None:
        while not self._stop.is_set():
            self._drain_batch()
            time.sleep(self.flush_interval)
        # final drain
        while True:
            n = self._drain_batch()
            if n == 0:
                break

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=30)

    def extra_stats(self) -> dict:
        with self._lock:
            return {
                "wb_max_queue": self._max_queue,
                "wb_flush_batches": self._flush_batches,
                "wb_flush_rows": self._flush_rows,
                "wb_pending_at_end": self._dirty.qsize(),
            }


STRATEGIES = {
    "cache_aside": CacheAside,
    "write_through": WriteThrough,
    "write_back": WriteBack,
}
