import uuid

from src.application.dto.user_status import UserStatusResponse
from src.domain.exceptions import UserNotFoundError
from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class GetUserStatusUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, user_id: uuid.UUID) -> UserStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(str(user_id))
            return UserStatusResponse.model_validate(user)
