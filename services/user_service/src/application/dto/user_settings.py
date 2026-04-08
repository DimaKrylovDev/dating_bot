import uuid

from pydantic import BaseModel, ConfigDict


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    language: str
    show_online_status: bool
    show_distance: bool
    show_age: bool
    discoverable: bool
    push_enabled: bool
    email_enabled: bool


class UpdateUserSettingsRequest(BaseModel):
    language: str | None = None
    show_online_status: bool | None = None
    show_distance: bool | None = None
    show_age: bool | None = None
    discoverable: bool | None = None
    push_enabled: bool | None = None
    email_enabled: bool | None = None
