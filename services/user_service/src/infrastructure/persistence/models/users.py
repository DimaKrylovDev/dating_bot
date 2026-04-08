import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.value_objects.user_status import UserStatus
from src.infrastructure.persistence.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True, index=True)

    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    ban_reason: Mapped[str | None] = mapped_column(nullable=True)
    banned_at: Mapped[datetime | None] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    is_premium: Mapped[bool] = mapped_column(nullable=False, default=False)
    premium_until: Mapped[datetime | None] = mapped_column(nullable=True)

    referral_code: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    referred_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now, onupdate=datetime.now
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True, index=True)

    language: Mapped[str] = mapped_column(nullable=False, default="ru")
    show_online_status: Mapped[bool] = mapped_column(nullable=False, default=True)
    show_distance: Mapped[bool] = mapped_column(nullable=False, default=True)
    show_age: Mapped[bool] = mapped_column(nullable=False, default=True)
    discoverable: Mapped[bool] = mapped_column(nullable=False, default=True)

    push_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    email_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now, onupdate=datetime.now
    )
