from src.persistance.repository.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistance.models.accounts import Accounts

class AccountsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Accounts)