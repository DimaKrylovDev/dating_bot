import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSettings:
    id: uuid.UUID
    user_id: uuid.UUID
    language: str = "ru"
    show_online_status: bool = True
    show_distance: bool = True
    show_age: bool = True
    discoverable: bool = True
    push_enabled: bool = True
    email_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
