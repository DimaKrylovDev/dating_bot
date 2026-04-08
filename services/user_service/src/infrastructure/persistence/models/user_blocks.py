import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.database import Base


class UserBlocks(Base):
    __tablename__ = "user_blocks"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_user_blocks_pair"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    blocker_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    blocked_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
