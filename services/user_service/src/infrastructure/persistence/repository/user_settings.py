import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.users import UserSettings
from src.infrastructure.persistence.repository.base import BaseRepository


class UserSettingsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=UserSettings)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        query = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalars().first()
