import uuid

from src.application.dto.user_settings import UpdateUserSettingsResponse, UserSettingsResponse
from src.domain.exceptions import UserSettingsNotFoundError
from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class UpdateUserSettingsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(
        self, user_id: uuid.UUID, data: UpdateUserSettingsResponse
    ) -> UserSettingsResponse:
        async with self._uow as uow:
            settings = await uow.user_settings.get_by_user_id(user_id)
            if settings is None:
                raise UserSettingsNotFoundError(str(user_id))

            values = data.model_dump(exclude_unset=True)
            updated = await uow.user_settings.update(settings.id, **values)
            await uow.commit()
            return UserSettingsResponse.model_validate(updated)
