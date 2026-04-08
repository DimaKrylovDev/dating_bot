import secrets
import uuid

from src.application.dto.referral import ReferralCodeResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import ReferralCodeAlreadyAssignedError, UserNotFoundError


class GenerateReferralCodeUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, user_id: uuid.UUID) -> ReferralCodeResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(str(user_id))
            if user.referral_code is not None:
                raise ReferralCodeAlreadyAssignedError(str(user_id))

            for _ in range(10):
                code = secrets.token_urlsafe(6)
                if await uow.users.get_by_referral_code(code) is None:
                    break
            else:
                raise RuntimeError("failed to generate unique referral code")

            updated = await uow.users.assign_referral_code(user_id, code)
            await uow.commit()
            return ReferralCodeResponse(user_id=user_id, code=updated.referral_code)
