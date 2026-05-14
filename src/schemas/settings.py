from pydantic import BaseModel, Field, ConfigDict, model_validator

from decimal import Decimal

from src.models.settings import Theme


class SettingsCreate(BaseModel):
    theme: Theme = Theme.LIGHT
    monthly_limit: Decimal | None = Field(default=None, ge=0)


class SettingsUpdate(BaseModel):
    theme: Theme | None = None
    monthly_limit: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_nullable_fields(self):
        if "theme" in self.model_fields_set and self.theme is None:
            raise ValueError("Theme cannot be null")

        return self
    # не пропустит Theme c значением Null


class SettingsRead(BaseModel):
    theme: Theme
    monthly_limit: Decimal | None

    model_config = ConfigDict(from_attributes=True)