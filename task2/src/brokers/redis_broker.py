from __future__ import annotations

import asyncio
from typing import AsyncIterator

import redis.asyncio as aioredis

from .base import Broker, BrokerConsumer, BrokerProducer


class RedisProducer(BrokerProducer):
    def __init__(self, url: str, queue: str) -> None:
        self._url = url
        self._queue = queue
        self._client: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._client = aioredis.from_url(self._url)

    async def publish(self, data: bytes) -> None:
        assert self._client is not None
        await self._client.lpush(self._queue, data)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()


class RedisConsumer(BrokerConsumer):
    def __init__(self, url: str, queue: str) -> None:
        self._url = url
        self._queue = queue
        self._client: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._client = aioredis.from_url(self._url)

    async def consume(self, stop: asyncio.Event) -> AsyncIterator[bytes]:
        assert self._client is not None
        while not stop.is_set():
            result = await self._client.brpop([self._queue], timeout=1)
            if result is not None:
                _, data = result
                yield data
        while True:
            data = await self._client.rpop(self._queue)
            if data is None:
                break
            yield data

    async def backlog(self) -> int:
        assert self._client is not None
        return int(await self._client.llen(self._queue))

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()


class RedisBroker(Broker):
    name = "redis"

    def __init__(self, url: str, queue: str = "bench") -> None:
        self._url = url
        self._queue = queue
        self._client: aioredis.Redis | None = None

    async def setup(self) -> None:
        self._client = aioredis.from_url(self._url)
        await self._client.ping()

    async def purge(self) -> None:
        assert self._client is not None
        await self._client.delete(self._queue)

    async def backlog(self) -> int:
        assert self._client is not None
        return int(await self._client.llen(self._queue))

    async def make_producer(self) -> BrokerProducer:
        p = RedisProducer(self._url, self._queue)
        await p.connect()
        return p

    async def make_consumer(self) -> BrokerConsumer:
        c = RedisConsumer(self._url, self._queue)
        await c.connect()
        return c

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
