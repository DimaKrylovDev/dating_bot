import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.value_objects.user_status import UserStatus


@dataclass
class User:
    id: uuid.UUID
    account_id: uuid.UUID
    status: UserStatus = UserStatus.ACTIVE
    ban_reason: str | None = None
    banned_at: datetime | None = None
    deleted_at: datetime | None = None
    is_premium: bool = False
    premium_until: datetime | None = None
    referral_code: str | None = None
    referred_by: uuid.UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
