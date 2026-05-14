from datetime import datetime, timezone
from decimal import Decimal
import enum
from email.policy import default

from pydantic import BaseModel, Field, ConfigDict, model_validator


class ExpenseCreate(BaseModel):
    category_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    expense_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str | None = Field(default=None, max_length=255)


class ExpenseUpdate(BaseModel):
    category_id: int | None = Field(default=None, gt=0)
    amount: Decimal | None = Field(default=None, gt=0)
    expense_date: datetime | None = None
    description: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_nullable_fields(self):
        not_nullable_fields = {
            "category_id": self.category_id,
            "amount": self.amount,
            "expense_date": self.expense_date,
        }

        for field_name, value in not_nullable_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"{field_name} cannot be null")

        return self


class ExpenseRead(BaseModel):
    id: int
    category: str
    amount: Decimal
    expense_date: datetime
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class ExpenseOrderBy(str, enum.Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    AMOUNT_ASC = "amount_asc"
    AMOUNT_DESC = "amount_desc"
    CATEGORY_ASC = "category_asc"
    CATEGORY_DESC = "category_desc"


class ExpenseFilter(BaseModel):
    category_id: int | None = Field(default=None, gt=0)

    date_from: datetime | None = None
    date_to: datetime | None = None

    amount_from: Decimal | None = Field(default=None, ge=0)
    amount_to: Decimal | None = Field(default=None, ge=0)

    order_by: ExpenseOrderBy = ExpenseOrderBy.NEWEST

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.date_from is not None and self.date_to is not None:
            if self.date_from > self.date_to:
                raise ValueError("date_from cannot be greater than date_to")

        if self.amount_from is not None and self.amount_to is not None:
            if self.amount_from > self.amount_to:
                raise ValueError("amount_from cannot be greater than amount_to")

        return self


# class ExpenseStats(BaseModel):
#     month: str
#     total: Decimal