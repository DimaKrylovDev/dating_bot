"""CLI runner. Example:
    python -m src.runner --strategy cache_aside --read-ratio 0.8 --duration 20 --workers 16 \
        --keys 1000 --out results/run.csv
"""
import argparse
import csv
import os
import random
import sys
import time
from pathlib import Path

from .app import STRATEGIES, WriteBack
from .cache import Cache, CacheCounters
from .db import DB, Counters


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--strategy", required=True, choices=list(STRATEGIES))
    p.add_argument("--read-ratio", type=float, required=True, help="0..1, share of GETs")
    p.add_argument("--duration", type=float, default=20.0)
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--keys", type=int, default=1000)
    p.add_argument("--value-size", type=int, default=64)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--label", default="run")
    p.add_argument("--out", default="results/results.csv")
    p.add_argument("--pg-dsn", default=os.environ.get("PG_DSN", "postgresql://bench:bench@localhost:5433/bench"))
    p.add_argument("--redis-url", default=os.environ.get("REDIS_URL", "redis://localhost:6380/0"))
    p.add_argument("--wb-flush-interval", type=float, default=0.5)
    p.add_argument("--wb-batch-size", type=int, default=200)
    return p.parse_args()


def make_keys(n: int) -> list[str]:
    return [f"k{i:06d}" for i in range(n)]


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)

    db_counters = Counters()
    cache_counters = CacheCounters()
    db = DB(args.pg_dsn, db_counters)
    cache = Cache(args.redis_url, cache_counters)

    print(f"[setup] strategy={args.strategy} read_ratio={args.read_ratio} "
          f"workers={args.workers} duration={args.duration}s keys={args.keys}", flush=True)

    db.init_schema()
    cache.flush()

    keys = make_keys(args.keys)
    seed_items = [(k, ("seed-" + str(rng.random()))[: args.value_size].ljust(args.value_size, "x")) for k in keys]
    db.seed(seed_items)
    print(f"[setup] seeded {len(seed_items)} rows in DB; cache flushed", flush=True)

    cls = STRATEGIES[args.strategy]
    if cls is WriteBack:
        app = cls(cache, db, flush_interval=args.wb_flush_interval, batch_size=args.wb_batch_size)
    else:
        app = cls(cache, db)

    # Reset counters AFTER seeding so we only measure the workload phase.
    db_counters.reads = 0
    db_counters.writes = 0
    cache_counters.hits = 0
    cache_counters.misses = 0
    cache_counters.sets = 0

    print(f"[run] starting load...", flush=True)
    from .load import run_load
    res = run_load(
        app=app,
        keys=keys,
        duration_s=args.duration,
        workers=args.workers,
        read_ratio=args.read_ratio,
        value_size=args.value_size,
        seed=args.seed,
    )
    print(f"[run] done in {res.duration:.2f}s, ops={res.ops}", flush=True)

    # For write-back: stop and force-drain so DB-write count is final.
    print(f"[stop] stopping app (drains write-back queue if any)...", flush=True)
    t_stop0 = time.monotonic()
    app.stop()
    stop_dur = time.monotonic() - t_stop0
    print(f"[stop] finished in {stop_dur:.2f}s", flush=True)

    db_snap = db_counters.snapshot()
    cache_snap = cache_counters.snapshot()
    extra = app.extra_stats()

    row = {
        "label": args.label,
        "strategy": args.strategy,
        "read_ratio": args.read_ratio,
        "workers": args.workers,
        "duration_target_s": args.duration,
        "duration_actual_s": round(res.duration, 3),
        "ops": res.ops,
        "reads": res.reads,
        "writes": res.writes,
        "throughput_rps": round(res.throughput, 1),
        "avg_latency_ms": round(res.avg_latency_ms, 3),
        "p50_ms": round(res.percentile_ms(0.50), 3),
        "p95_ms": round(res.percentile_ms(0.95), 3),
        "p99_ms": round(res.percentile_ms(0.99), 3),
        **db_snap,
        **cache_snap,
        **extra,
        "stop_drain_s": round(stop_dur, 3),
    }

    print("[result] " + ", ".join(f"{k}={v}" for k, v in row.items()), flush=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_path.exists() or out_path.stat().st_size == 0
    fields = [
        "label", "strategy", "read_ratio", "workers",
        "duration_target_s", "duration_actual_s",
        "ops", "reads", "writes",
        "throughput_rps", "avg_latency_ms", "p50_ms", "p95_ms", "p99_ms",
        "db_reads", "db_writes",
        "cache_hits", "cache_misses", "cache_sets", "hit_rate",
        "wb_max_queue", "wb_flush_batches", "wb_flush_rows", "wb_pending_at_end",
        "stop_drain_s",
    ]
    with out_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            w.writeheader()
        # fill missing fields
        for k in fields:
            row.setdefault(k, "")
        w.writerow(row)
    print(f"[out] appended to {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
