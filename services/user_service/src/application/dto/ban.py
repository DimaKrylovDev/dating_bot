import uuid

from pydantic import BaseModel


class BanUserRequest(BaseModel):
    user_id: uuid.UUID
    reason: str
