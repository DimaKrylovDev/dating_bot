import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserBlock:
    id: uuid.UUID
    blocker_id: uuid.UUID
    blocked_id: uuid.UUID
    created_at: datetime = field(default_factory=datetime.now)
