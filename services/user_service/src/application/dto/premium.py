import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PremiumStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_premium: bool
    premium_until: datetime | None = None


class ActivatePremiumRequest(BaseModel):
    user_id: uuid.UUID
    days: int
