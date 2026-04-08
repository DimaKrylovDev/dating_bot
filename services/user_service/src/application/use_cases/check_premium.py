import uuid
from datetime import datetime

from src.application.dto.premium import PremiumStatusResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import UserNotFoundError


class CheckPremiumUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, user_id: uuid.UUID) -> PremiumStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(str(user_id))

            active = bool(
                user.is_premium and user.premium_until and user.premium_until > datetime.now()
            )
            if user.is_premium and not active:
                await uow.users.deactivate_premium(user_id)
                await uow.commit()

            return PremiumStatusResponse(
                id=user.id,
                is_premium=active,
                premium_until=user.premium_until,
            )
