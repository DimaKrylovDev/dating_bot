import uuid
from typing import Type, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.base import AbstractBaseRepository

T = TypeVar("T")


class BaseRepository(AbstractBaseRepository):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model

    async def create(self, **values):
        query = insert(self._model).values(**values).returning(self._model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, id_: uuid.UUID):
        query = select(self._model).where(self._model.id == id_)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_one_or_none(self, **filters):
        query = select(self._model).filter_by(**filters)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_all_by_filter(self, **filters):
        query = select(self._model).filter_by(**filters)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def delete(self, id_: uuid.UUID):
        query = delete(self._model).where(self._model.id == id_).returning(self._model)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def update(self, id_: uuid.UUID, **values):
        query = (
            update(self._model)
            .where(self._model.id == id_)
            .values(**values)
            .returning(self._model)
        )
        result = await self._session.execute(query)
        return result.scalars().first()
