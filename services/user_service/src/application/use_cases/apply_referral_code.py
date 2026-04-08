from datetime import datetime, timedelta

from src.application.dto.referral import ApplyReferralCodeRequest, ReferralApplyResponse
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.exceptions import (
    AlreadyReferredError,
    ReferralCodeNotFoundError,
    SelfReferralError,
    UserNotFoundError,
)
from src.domain.value_objects.referral_bonus_type import (
    REFERRAL_BONUS_PREMIUM_DAYS,
    REFERRAL_BONUS_SUPER_LIKES,
    ReferralBonusType,
)


class ApplyReferralCodeUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __call__(self, data: ApplyReferralCodeRequest) -> ReferralApplyResponse:
        async with self._uow as uow:
            user = await uow.users.get_by_id(data.user_id)
            if user is None:
                raise UserNotFoundError(str(data.user_id))
            if user.referred_by is not None:
                raise AlreadyReferredError(str(data.user_id))

            referrer = await uow.users.get_by_referral_code(data.code)
            if referrer is None:
                raise ReferralCodeNotFoundError(data.code)
            if referrer.id == user.id:
                raise SelfReferralError(str(user.id))

            await uow.users.set_referred_by(user.id, referrer.id)

            if REFERRAL_BONUS_PREMIUM_DAYS > 0:
                base = (
                    user.premium_until
                    if user.premium_until and user.premium_until > datetime.now()
                    else datetime.now()
                )
                new_until = base + timedelta(days=REFERRAL_BONUS_PREMIUM_DAYS)
                await uow.users.activate_premium(user.id, new_until)

                await uow.referral_bonuses.create(
                    user_id=user.id,
                    referrer_id=referrer.id,
                    bonus_type=ReferralBonusType.PREMIUM_DAYS,
                    amount=REFERRAL_BONUS_PREMIUM_DAYS,
                )

            if REFERRAL_BONUS_SUPER_LIKES > 0:
                await uow.referral_bonuses.create(
                    user_id=user.id,
                    referrer_id=referrer.id,
                    bonus_type=ReferralBonusType.SUPER_LIKES,
                    amount=REFERRAL_BONUS_SUPER_LIKES,
                )

            await uow.commit()
            return ReferralApplyResponse(
                user_id=user.id,
                referrer_id=referrer.id,
                premium_days_granted=REFERRAL_BONUS_PREMIUM_DAYS,
                super_likes_granted=REFERRAL_BONUS_SUPER_LIKES,
            )
