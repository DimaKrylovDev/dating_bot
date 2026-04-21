from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator


class BrokerProducer(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def publish(self, data: bytes) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...


class BrokerConsumer(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def consume(self, stop: asyncio.Event) -> AsyncIterator[bytes]: ...

    @abstractmethod
    async def backlog(self) -> int: ...

    @abstractmethod
    async def close(self) -> None: ...


class Broker(ABC):
    name: str

    @abstractmethod
    async def setup(self) -> None: ...

    @abstractmethod
    async def purge(self) -> None: ...

    @abstractmethod
    async def backlog(self) -> int: ...

    @abstractmethod
    async def make_producer(self) -> BrokerProducer: ...

    @abstractmethod
    async def make_consumer(self) -> BrokerConsumer: ...

    @abstractmethod
    async def close(self) -> None: ...
