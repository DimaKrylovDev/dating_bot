import uuid

from src.application.dto.premium import PremiumStatusResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import UserNotFoundError


class DeactivatePremiumUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, user_id: uuid.UUID) -> PremiumStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(str(user_id))
            updated = await uow.users.deactivate_premium(user_id)
            await uow.commit()
            return PremiumStatusResponse.model_validate(updated)
