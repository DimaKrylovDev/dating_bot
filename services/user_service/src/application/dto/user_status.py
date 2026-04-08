import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.value_objects.user_status import UserStatus


class UserStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: UserStatus
    ban_reason: str | None = None
    banned_at: datetime | None = None
    deleted_at: datetime | None = None


class UpdateUserStatusRequest(BaseModel):
    status: UserStatus
    reason: str | None = None
