import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.value_objects.referral_bonus_type import ReferralBonusType


@dataclass
class ReferralBonus:
    id: uuid.UUID
    user_id: uuid.UUID
    referrer_id: uuid.UUID
    bonus_type: ReferralBonusType
    amount: int
    created_at: datetime = field(default_factory=datetime.now)
