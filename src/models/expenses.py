from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, TIMESTAMP, ForeignKey, CheckConstraint

from datetime import datetime, timezone

from decimal import Decimal

from src.core.database import Base


class ExpensesOrm(Base):
    __tablename__ = "expenses"

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
    )

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id:Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    amount:Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    expense_date:Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    description:Mapped[str | None] = mapped_column(String(255), nullable=True)

    category = relationship(
        "CategoriesOrm",
        back_populates="expenses"
    )

    user = relationship(
        "UsersOrm",
        back_populates="expenses"
    )