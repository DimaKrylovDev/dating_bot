import uuid

from pydantic import BaseModel, ConfigDict


class UserBlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    blocker_id: uuid.UUID
    blocked_id: uuid.UUID


class BlockPairRequest(BaseModel):
    blocker_id: uuid.UUID
    blocked_id: uuid.UUID
