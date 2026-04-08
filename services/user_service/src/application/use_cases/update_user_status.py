import uuid

from src.application.dto.user_status import UpdateUserStatusResponse, UserStatusResponse
from src.domain.exceptions import UserNotFoundError
from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class UpdateUserStatusUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(
        self, user_id: uuid.UUID, data: UpdateUserStatusResponse
    ) -> UserStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(str(user_id))

            updated = await uow.users.set_status(user_id, data.status, data.reason)
            await uow.commit()
            return UserStatusResponse.model_validate(updated)
