import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.value_objects.referral_bonus_type import ReferralBonusType
from src.infrastructure.persistence.database import Base


class ReferralBonuses(Base):
    __tablename__ = "referral_bonuses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    referrer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    bonus_type: Mapped[ReferralBonusType] = mapped_column(
        SAEnum(ReferralBonusType, name="referral_bonus_type"),
        nullable=False,
    )
    amount: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
