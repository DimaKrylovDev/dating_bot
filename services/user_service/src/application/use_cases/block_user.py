from src.application.dto.blocks import BlockPairRequest, UserBlockResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import (
    CannotBlockSelfError,
    UserAlreadyBlockedError,
    UserNotFoundError,
)


class BlockUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, data: BlockPairRequest) -> UserBlockResponse:
        if data.blocker_id == data.blocked_id:
            raise CannotBlockSelfError(str(data.blocker_id))

        async with self._uow as uow:
            for uid in (data.blocker_id, data.blocked_id):
                if await uow.users.get_by_id(uid) is None:
                    raise UserNotFoundError(str(uid))

            if await uow.user_blocks.is_blocked(data.blocker_id, data.blocked_id):
                raise UserAlreadyBlockedError(str(data.blocked_id))

            block = await uow.user_blocks.create(
                blocker_id=data.blocker_id,
                blocked_id=data.blocked_id,
            )
            await uow.commit()
            return UserBlockResponse.model_validate(block)
