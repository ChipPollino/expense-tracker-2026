from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, Numeric, ForeignKey, CheckConstraint

from src.core.database import Base

from decimal import Decimal

import enum


class Theme(enum.Enum):
    LIGHT = "light"
    DARK = "dark"


class SettingsOrm(Base):
    __tablename__ = "settings"

    __table_args__ = (
        CheckConstraint(
            "monthly_limit IS NULL OR monthly_limit >= 0",
            name="check_monthly_limit_positive"),
    )

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    theme:Mapped[Theme] = mapped_column(Enum(Theme), nullable=False, default=Theme.LIGHT)
    monthly_limit:Mapped[Decimal | None] = mapped_column(
        Numeric(10,2),
        nullable=True,
        default=None
    )

    user = relationship(
        "UsersOrm",
        back_populates="settings"
    )