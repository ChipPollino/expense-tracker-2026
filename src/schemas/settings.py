from pydantic import BaseModel, Field, ConfigDict

from decimal import Decimal

from src.models.settings import Theme


class SettingsUpdate(BaseModel):
    theme: Theme | None = None
    monthly_limit: Decimal | None = Field(default=None, ge=0)


class SettingsRead(BaseModel):
    theme: Theme
    monthly_limit: Decimal | None

    model_config = ConfigDict(from_attributes=True)