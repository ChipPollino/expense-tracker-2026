from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TEXT
from sqlalchemy_utils import EmailType
from src.core.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(100), nullable=False)
    email:Mapped[str] = mapped_column(EmailType, unique=True, nullable=False, index=True)
    password_hash:Mapped[str] = mapped_column(TEXT, nullable=False)

    expenses = relationship(
        "ExpensesOrm",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    settings = relationship(
        "SettingsOrm",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )

    categories = relationship(
        "CategoriesOrm",
        back_populates="user",
        cascade="all, delete-orphan")