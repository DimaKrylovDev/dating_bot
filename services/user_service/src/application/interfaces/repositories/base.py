import uuid
from abc import ABC, abstractmethod


class AbstractBaseRepository(ABC):
    @abstractmethod
    async def create(self, **values): ...

    @abstractmethod
    async def get_by_id(self, id_: uuid.UUID): ...

    @abstractmethod
    async def get_one_or_none(self, **filters): ...

    @abstractmethod
    async def get_all_by_filter(self, **filters): ...

    @abstractmethod
    async def delete(self, id_: uuid.UUID): ...

    @abstractmethod
    async def update(self, id_: uuid.UUID, **values): ...
