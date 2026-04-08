from datetime import datetime, timedelta

from src.application.dto.premium import ActivatePremiumRequest, PremiumStatusResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import UserNotFoundError


class ActivatePremiumUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, data: ActivatePremiumRequest) -> PremiumStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(data.user_id)
            if user is None:
                raise UserNotFoundError(str(data.user_id))

            base = (
                user.premium_until
                if user.premium_until and user.premium_until > datetime.now()
                else datetime.now()
            )
            until = base + timedelta(days=data.days)
            updated = await uow.users.activate_premium(data.user_id, until)
            await uow.commit()
            return PremiumStatusResponse.model_validate(updated)
