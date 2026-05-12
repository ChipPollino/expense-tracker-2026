from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, UniqueConstraint, ForeignKey

from src.core.database import Base

class CategoriesOrm(Base):
    __tablename__ = "categories"

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_category_name"),
    )

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name:Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    user = relationship(
        "UsersOrm",
        back_populates="categories",
    )

    expenses = relationship(
        "ExpensesOrm",
        back_populates="category"
    )