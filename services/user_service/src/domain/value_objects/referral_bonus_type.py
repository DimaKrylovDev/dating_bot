import enum


class ReferralBonusType(str, enum.Enum):
    PREMIUM_DAYS = "premium_days"
    SUPER_LIKES = "super_likes"


REFERRAL_BONUS_PREMIUM_DAYS = 1
REFERRAL_BONUS_SUPER_LIKES = 0
