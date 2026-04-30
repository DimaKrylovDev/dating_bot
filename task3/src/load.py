"""Load generator: N worker threads, fixed duration, mixed read/write ratio."""
import random
import threading
import time
from dataclasses import dataclass


@dataclass
class LoadResult:
    ops: int
    reads: int
    writes: int
    duration: float
    latencies_ns: list[int]

    @property
    def throughput(self) -> float:
        return self.ops / self.duration if self.duration > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies_ns:
            return 0.0
        return (sum(self.latencies_ns) / len(self.latencies_ns)) / 1_000_000

    def percentile_ms(self, p: float) -> float:
        if not self.latencies_ns:
            return 0.0
        s = sorted(self.latencies_ns)
        idx = min(len(s) - 1, max(0, int(len(s) * p)))
        return s[idx] / 1_000_000


def run_load(
    app,
    keys: list[str],
    duration_s: float,
    workers: int,
    read_ratio: float,
    value_size: int = 64,
    seed: int = 42,
) -> LoadResult:
    stop_at = time.monotonic() + duration_s
    counters = {"ops": 0, "reads": 0, "writes": 0}
    counters_lock = threading.Lock()
    latencies: list[int] = []
    lat_locks = threading.Lock()

    def worker(wid: int) -> None:
        rng = random.Random(seed + wid)
        local_lat: list[int] = []
        local_ops = local_reads = local_writes = 0
        payload_pool = [
            ("v" + str(rng.random()))[:value_size].ljust(value_size, "x")
            for _ in range(32)
        ]
        while time.monotonic() < stop_at:
            k = rng.choice(keys)
            is_read = rng.random() < read_ratio
            t0 = time.perf_counter_ns()
            if is_read:
                app.get(k)
                local_reads += 1
            else:
                app.set(k, rng.choice(payload_pool))
                local_writes += 1
            local_lat.append(time.perf_counter_ns() - t0)
            local_ops += 1
        with counters_lock:
            counters["ops"] += local_ops
            counters["reads"] += local_reads
            counters["writes"] += local_writes
        with lat_locks:
            latencies.extend(local_lat)

    threads = [threading.Thread(target=worker, args=(i,), name=f"w{i}") for i in range(workers)]
    t0 = time.monotonic()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    dur = time.monotonic() - t0
    return LoadResult(
        ops=counters["ops"],
        reads=counters["reads"],
        writes=counters["writes"],
        duration=dur,
        latencies_ns=latencies,
    )
