import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.referral_bonuses import ReferralBonuses
from src.infrastructure.persistence.repository.base import BaseRepository


class ReferralBonusesRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ReferralBonuses)

    async def list_for_user(self, user_id: uuid.UUID) -> list[ReferralBonuses]:
        query = select(ReferralBonuses).where(ReferralBonuses.user_id == user_id)
        result = await self._session.execute(query)
        return list(result.scalars().all())
