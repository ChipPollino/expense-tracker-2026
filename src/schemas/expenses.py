from datetime import datetime
from decimal import Decimal
# import enum

from pydantic import BaseModel, Field, ConfigDict


class ExpenseCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    expense_date: datetime | None = None
    description: str | None = Field(default=None, max_length=255)


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    expense_date: datetime | None = None
    description: str | None = Field(default=None, max_length=255)


class ExpenseRead(BaseModel):
    id: int
    category: str
    amount: Decimal
    expense_date: datetime
    description: str | None

    model_config = ConfigDict(from_attributes=True)


# class ExpenseOrderBy(str, enum.Enum):
#     NEWEST = "newest"
#     OLDEST = "oldest"
#     AMOUNT_ASC = "amount_asc"
#     AMOUNT_DESC = "amount_desc"
#     CATEGORY_ASC = "category_asc"
#     CATEGORY_DESC = "category_desc"

# class ExpenseFilter(BaseModel):
#     category: str | None = Field(default=None, max_length=100)

#     date_from: datetime | None = None
#     date_to: datetime | None = None

#     amount_from: Decimal | None = Field(default=None, ge=0)
#     amount_to: Decimal | None = Field(default=None, ge=0)

#     order_by: ExpenseOrderBy | None = None



# class ExpenseStats(BaseModel):
#     month: str
#     total: Decimal