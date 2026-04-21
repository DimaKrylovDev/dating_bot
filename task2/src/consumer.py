from __future__ import annotations

import asyncio
import time

from .brokers.base import BrokerConsumer
from .message import parse_message
from .metrics import Metrics


async def run_consumer(
    consumer: BrokerConsumer,
    metrics: Metrics,
    stop: asyncio.Event,
) -> None:
    async for data in consumer.consume(stop):
        recv_ts = time.time()
        try:
            _, ts = parse_message(data)
            metrics.add_latency(max(0.0, recv_ts - ts))
            metrics.received += 1
        except Exception:
            metrics.recv_errors += 1
