import threading
import psycopg


class Counters:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reads = 0
        self.writes = 0

    def inc_read(self, n: int = 1) -> None:
        with self._lock:
            self.reads += n

    def inc_write(self, n: int = 1) -> None:
        with self._lock:
            self.writes += n

    def snapshot(self) -> dict:
        with self._lock:
            return {"db_reads": self.reads, "db_writes": self.writes}


class DB:
    """Thin Postgres KV wrapper that counts every real DB call."""

    def __init__(self, dsn: str, counters: Counters) -> None:
        self.dsn = dsn
        self.counters = counters
        self._local = threading.local()

    def _conn(self) -> psycopg.Connection:
        c = getattr(self._local, "conn", None)
        if c is None or c.closed:
            c = psycopg.connect(self.dsn, autocommit=True)
            self._local.conn = c
        return c

    def init_schema(self) -> None:
        with psycopg.connect(self.dsn, autocommit=True) as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS kv ("
                "  key TEXT PRIMARY KEY,"
                "  value TEXT NOT NULL,"
                "  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                ")"
            )
            c.execute("TRUNCATE kv")

    def seed(self, items: list[tuple[str, str]]) -> None:
        with psycopg.connect(self.dsn, autocommit=True) as c, c.cursor() as cur:
            cur.executemany(
                "INSERT INTO kv(key, value) VALUES (%s, %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                items,
            )

    def get(self, key: str) -> str | None:
        self.counters.inc_read()
        with self._conn().cursor() as cur:
            cur.execute("SELECT value FROM kv WHERE key = %s", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        self.counters.inc_write()
        with self._conn().cursor() as cur:
            cur.execute(
                "INSERT INTO kv(key, value, updated_at) VALUES (%s, %s, now()) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
                (key, value),
            )

    def set_many(self, items: list[tuple[str, str]]) -> None:
        if not items:
            return
        self.counters.inc_write(len(items))
        with self._conn().cursor() as cur:
            cur.executemany(
                "INSERT INTO kv(key, value, updated_at) VALUES (%s, %s, now()) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
                items,
            )

    def total_rows(self) -> int:
        with psycopg.connect(self.dsn, autocommit=True) as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM kv")
            return cur.fetchone()[0]
