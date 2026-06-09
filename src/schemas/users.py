from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserCreateDB(UserBase):
    password_hash: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_nullable_fields(self):
        not_nullable_fields = {
            "name": self.name,
            "email": self.email,
        }

        for field_name, value in not_nullable_fields.items():
            if field_name in self.model_fields_set and value is None:
                raise ValueError(f"{field_name} cannot be null")

        return self


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

class PasswordHashUpdate(BaseModel):
    password_hash: str


class UserRead(UserBase):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)