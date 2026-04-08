from src.application.dto.ban import BanUserRequest
from src.application.dto.user_status import UserStatusResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import UserNotFoundError
from src.domain.value_objects.user_status import UserStatus


class BanUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, data: BanUserRequest) -> UserStatusResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(data.user_id)
            if user is None:
                raise UserNotFoundError(str(data.user_id))

            updated = await uow.users.set_status(data.user_id, UserStatus.BANNED, data.reason)
            await uow.commit()
            return UserStatusResponse.model_validate(updated)
