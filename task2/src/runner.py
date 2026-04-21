from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
import time
from pathlib import Path

from .brokers.base import Broker
from .brokers.rabbitmq import RabbitBroker
from .brokers.redis_broker import RedisBroker
from .consumer import run_consumer
from .metrics import Metrics
from .producer import run_producer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RabbitMQ vs Redis broker benchmark")
    p.add_argument("--broker", choices=["rabbit", "redis"], required=True)
    p.add_argument("--rate", type=int, required=True, help="target msg/sec total across producers")
    p.add_argument("--size", type=int, required=True, help="message size in bytes")
    p.add_argument("--duration", type=float, required=True, help="producer duration, seconds")
    p.add_argument("--producers", type=int, default=1)
    p.add_argument("--consumers", type=int, default=1)
    p.add_argument("--drain-timeout", type=float, default=30.0, help="max seconds to wait for consumers to drain")
    p.add_argument("--out", type=str, default="/app/results/results.csv")
    p.add_argument("--tag", type=str, default="", help="free-form label stored in result row")
    return p.parse_args()


def build_broker(kind: str) -> Broker:
    if kind == "rabbit":
        url = os.environ.get("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
        return RabbitBroker(url)
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisBroker(url)


async def run(args: argparse.Namespace) -> dict:
    broker = build_broker(args.broker)
    await broker.setup()
    await broker.purge()

    metrics = Metrics()
    stop_producers = asyncio.Event()
    stop_consumers = asyncio.Event()

    producers = [await broker.make_producer() for _ in range(args.producers)]
    consumers = [await broker.make_consumer() for _ in range(args.consumers)]

    per_prod_rate = max(1, args.rate // args.producers)

    prod_tasks = [
        asyncio.create_task(
            run_producer(
                p,
                metrics,
                rate=per_prod_rate,
                duration=args.duration,
                size=args.size,
                seq_start=i,
                seq_step=args.producers,
            )
        )
        for i, p in enumerate(producers)
    ]
    cons_tasks = [asyncio.create_task(run_consumer(c, metrics, stop_consumers)) for c in consumers]

    wall_start = time.perf_counter()
    await asyncio.gather(*prod_tasks, return_exceptions=True)
    produce_elapsed = time.perf_counter() - wall_start

    drain_start = time.perf_counter()
    while time.perf_counter() - drain_start < args.drain_timeout:
        backlog = await broker.backlog()
        if backlog == 0 and metrics.received >= metrics.sent:
            break
        await asyncio.sleep(0.5)
    final_backlog = await broker.backlog()

    stop_consumers.set()
    await asyncio.gather(*cons_tasks, return_exceptions=True)

    for p in producers:
        await p.close()
    for c in consumers:
        await c.close()
    await broker.close()

    total_elapsed = time.perf_counter() - wall_start
    snap = metrics.snapshot()
    row = {
        "broker": broker.name,
        "tag": args.tag,
        "target_rate": args.rate,
        "size": args.size,
        "duration_s": args.duration,
        "producers": args.producers,
        "consumers": args.consumers,
        "produce_elapsed_s": round(produce_elapsed, 3),
        "total_elapsed_s": round(total_elapsed, 3),
        "sent": snap["sent"],
        "received": snap["received"],
        "lost_or_backlog": max(0, snap["sent"] - snap["received"]),
        "final_backlog": final_backlog,
        "send_errors": snap["send_errors"],
        "recv_errors": snap["recv_errors"],
        "send_rate_msg_s": round(snap["sent"] / produce_elapsed, 1) if produce_elapsed > 0 else 0,
        "recv_rate_msg_s": round(snap["received"] / total_elapsed, 1) if total_elapsed > 0 else 0,
        "avg_latency_ms": round(snap["avg_latency_ms"], 2),
        "p50_latency_ms": round(snap["p50_latency_ms"], 2),
        "p95_latency_ms": round(snap["p95_latency_ms"], 2),
        "p99_latency_ms": round(snap["p99_latency_ms"], 2),
        "max_latency_ms": round(snap["max_latency_ms"], 2),
    }
    return row


def append_csv(path: str, row: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out.exists()
    with out.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new_file:
            w.writeheader()
        w.writerow(row)


def main() -> None:
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        pass

    args = parse_args()
    row = asyncio.run(run(args))
    print(json.dumps(row, indent=2))
    append_csv(args.out, row)


if __name__ == "__main__":
    sys.exit(main())
