import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.user_status import UserStatus
from src.infrastructure.persistence.models.users import Users
from src.infrastructure.persistence.repository.base import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Users)

    async def get_by_account_id(self, account_id: uuid.UUID) -> Users | None:
        query = select(Users).where(Users.account_id == account_id)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_by_referral_code(self, code: str) -> Users | None:
        query = select(Users).where(Users.referral_code == code)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def assign_referral_code(self, id_: uuid.UUID, code: str) -> Users | None:
        user = await self.get_by_id(id_)
        if user is None or user.referral_code is not None:
            return user
        return await self.update(id_, referral_code=code)

    async def activate_premium(self, id_: uuid.UUID, until: datetime) -> Users | None:
        return await self.update(id_, is_premium=True, premium_until=until)

    async def deactivate_premium(self, id_: uuid.UUID) -> Users | None:
        return await self.update(id_, is_premium=False, premium_until=None)

    async def set_referred_by(self, id_: uuid.UUID, referrer_id: uuid.UUID) -> Users | None:
        return await self.update(id_, referred_by=referrer_id)

    async def set_status(
        self,
        id_: uuid.UUID,
        status: UserStatus,
        reason: str | None = None,
    ) -> Users | None:
        values: dict = {"status": status}
        if status == UserStatus.BANNED:
            values["ban_reason"] = reason
            values["banned_at"] = datetime.now()
        elif status == UserStatus.DELETED:
            values["deleted_at"] = datetime.now()
        return await self.update(id_, **values)
