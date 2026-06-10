from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator


class AnalyticsPeriod(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_period(self):
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError("date_from cannot be greater than date_to")

        return self


class AnalyticsSummary(BaseModel):
    total: Decimal
    expenses_count: int


class CategoryExpenseStats(BaseModel):
    category_id: int
    category: str
    total: Decimal


class MonthlyExpenseStats(BaseModel):
    month: str
    total: Decimal