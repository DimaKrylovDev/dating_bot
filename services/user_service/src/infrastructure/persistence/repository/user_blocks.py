import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.user_blocks import UserBlocks
from src.infrastructure.persistence.repository.base import BaseRepository


class UserBlocksRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=UserBlocks)

    async def list_blocked_by(self, blocker_id: uuid.UUID) -> list[UserBlocks]:
        query = select(UserBlocks).where(UserBlocks.blocker_id == blocker_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def list_blocked_ids(self, blocker_id: uuid.UUID) -> list[uuid.UUID]:
        query = select(UserBlocks.blocked_id).where(UserBlocks.blocker_id == blocker_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def delete_pair(self, blocker_id: uuid.UUID, blocked_id: uuid.UUID) -> None:
        query = delete(UserBlocks).where(
            UserBlocks.blocker_id == blocker_id,
            UserBlocks.blocked_id == blocked_id,
        )
        await self._session.execute(query)

    async def is_blocked(self, blocker_id: uuid.UUID, blocked_id: uuid.UUID) -> bool:
        query = select(UserBlocks.id).where(
            UserBlocks.blocker_id == blocker_id,
            UserBlocks.blocked_id == blocked_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None
