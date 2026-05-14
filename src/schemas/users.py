from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserCreateDB(UserBase):
    password_hash: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None


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