from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.persistence.repository.referral_bonuses import ReferralBonusesRepository
from src.infrastructure.persistence.repository.user_blocks import UserBlocksRepository
from src.infrastructure.persistence.repository.user_settings import UserSettingsRepository
from src.infrastructure.persistence.repository.users import UsersRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_maker: async_sessionmaker):
        self._session_maker = session_maker

    async def __aenter__(self):
        self._session = self._session_maker()
        self.users = UsersRepository(self._session)
        self.user_settings = UserSettingsRepository(self._session)
        self.referral_bonuses = ReferralBonusesRepository(self._session)
        self.user_blocks = UserBlocksRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
