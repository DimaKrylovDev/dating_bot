import threading
import redis


class CacheCounters:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.sets = 0

    def inc_hit(self) -> None:
        with self._lock:
            self.hits += 1

    def inc_miss(self) -> None:
        with self._lock:
            self.misses += 1

    def inc_set(self, n: int = 1) -> None:
        with self._lock:
            self.sets += n

    def snapshot(self) -> dict:
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total) if total else 0.0
            return {
                "cache_hits": self.hits,
                "cache_misses": self.misses,
                "cache_sets": self.sets,
                "hit_rate": round(hit_rate, 4),
            }


class Cache:
    """Redis wrapper with hit/miss accounting."""

    def __init__(self, url: str, counters: CacheCounters) -> None:
        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.counters = counters

    def flush(self) -> None:
        self.client.flushdb()

    def get(self, key: str) -> str | None:
        v = self.client.get(key)
        if v is None:
            self.counters.inc_miss()
        else:
            self.counters.inc_hit()
        return v

    def set(self, key: str, value: str) -> None:
        self.counters.inc_set()
        self.client.set(key, value)
