from __future__ import annotations

import asyncio
import time

from .brokers.base import BrokerProducer
from .message import make_message
from .metrics import Metrics


async def run_producer(
    producer: BrokerProducer,
    metrics: Metrics,
    rate: int,
    duration: float,
    size: int,
    seq_start: int = 0,
    seq_step: int = 1,
) -> None:
    interval = 1.0 / rate
    start = time.perf_counter()
    deadline = start + duration
    seq = seq_start
    next_at = start

    while True:
        now = time.perf_counter()
        if now >= deadline:
            return
        if now < next_at:
            await asyncio.sleep(min(next_at - now, 0.005))
            continue

        behind = int((now - next_at) / interval) + 1
        batch = min(behind, 256)

        for _ in range(batch):
            data = make_message(seq, size)
            try:
                await producer.publish(data)
                metrics.sent += 1
            except Exception:
                metrics.send_errors += 1
            seq += seq_step

        next_at += batch * interval
