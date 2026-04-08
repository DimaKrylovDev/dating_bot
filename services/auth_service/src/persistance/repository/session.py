from sqlalchemy.ext.asyncio import AsyncSession

from src.persistance.models.session import Session
from src.persistance.repository.base import BaseRepository


class SessionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Session)
