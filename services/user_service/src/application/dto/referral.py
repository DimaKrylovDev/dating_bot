import uuid

from pydantic import BaseModel


class ReferralCodeResponse(BaseModel):
    user_id: uuid.UUID
    code: str


class ApplyReferralCodeRequest(BaseModel):
    user_id: uuid.UUID
    code: str


class ReferralApplyResponse(BaseModel):
    user_id: uuid.UUID
    referrer_id: uuid.UUID
    premium_days_granted: int
    super_likes_granted: int
