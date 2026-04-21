from __future__ import annotations

import asyncio
from typing import AsyncIterator

import aio_pika

from .base import Broker, BrokerConsumer, BrokerProducer


class RabbitProducer(BrokerProducer):
    def __init__(self, url: str, queue: str) -> None:
        self._url = url
        self._queue = queue
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel(publisher_confirms=False)
        self._exchange = self._channel.default_exchange

    async def publish(self, data: bytes) -> None:
        assert self._exchange is not None
        msg = aio_pika.Message(body=data, delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT)
        await self._exchange.publish(msg, routing_key=self._queue, mandatory=False)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()


class RabbitConsumer(BrokerConsumer):
    def __init__(self, url: str, queue: str, prefetch: int = 200) -> None:
        self._url = url
        self._queue_name = queue
        self._prefetch = prefetch
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._prefetch)
        self._queue = await self._channel.declare_queue(self._queue_name, durable=False, auto_delete=False)

    async def consume(self, stop: asyncio.Event) -> AsyncIterator[bytes]:
        assert self._queue is not None
        async with self._queue.iterator() as it:
            while not stop.is_set():
                try:
                    message = await asyncio.wait_for(it.__anext__(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    break
                async with message.process():
                    yield message.body

    async def backlog(self) -> int:
        assert self._channel is not None
        q = await self._channel.declare_queue(self._queue_name, durable=False, auto_delete=False, passive=True)
        return q.declaration_result.message_count

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()


class RabbitBroker(Broker):
    name = "rabbitmq"

    def __init__(self, url: str, queue: str = "bench") -> None:
        self._url = url
        self._queue = queue
        self._admin_conn: aio_pika.RobustConnection | None = None
        self._admin_ch: aio_pika.abc.AbstractChannel | None = None

    async def setup(self) -> None:
        self._admin_conn = await aio_pika.connect_robust(self._url)
        self._admin_ch = await self._admin_conn.channel()
        await self._admin_ch.declare_queue(self._queue, durable=False, auto_delete=False)

    async def purge(self) -> None:
        assert self._admin_ch is not None
        q = await self._admin_ch.declare_queue(self._queue, durable=False, auto_delete=False)
        await q.purge()

    async def backlog(self) -> int:
        assert self._admin_ch is not None
        q = await self._admin_ch.declare_queue(self._queue, durable=False, auto_delete=False, passive=True)
        return q.declaration_result.message_count

    async def make_producer(self) -> BrokerProducer:
        p = RabbitProducer(self._url, self._queue)
        await p.connect()
        return p

    async def make_consumer(self) -> BrokerConsumer:
        c = RabbitConsumer(self._url, self._queue)
        await c.connect()
        return c

    async def close(self) -> None:
        if self._admin_conn is not None:
            await self._admin_conn.close()
