from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UsersOrm
from src.repositories.settings import SettingsRepository
from src.repositories.users import UsersRepository
from src.schemas.settings import SettingsCreate
from src.schemas.users import (
    PasswordChange,
    PasswordHashUpdate,
    UserCreate,
    UserCreateDB,
    UserLogin,
)


password_hasher = PasswordHash.recommended()


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidOldPasswordError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_repo = UsersRepository(session)
        self.settings_repo = SettingsRepository(session)

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hasher.hash(password)

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return password_hasher.verify(plain_password, password_hash)

    async def register(self, data: UserCreate) -> UsersOrm:
        existing_user = await self.users_repo.get_by_email(str(data.email))

        if existing_user is not None:
            raise EmailAlreadyRegisteredError("Email already registered")

        user_data = UserCreateDB(
            name=data.name,
            email=data.email,
            password_hash=self.hash_password(data.password),
        )

        try:
            user = await self.users_repo.add(user_data)

            await self.settings_repo.add(
                data=SettingsCreate(),
                user_id=user.id,
            )

            await self.session.commit()

        except IntegrityError as error:
            await self.session.rollback()
            raise EmailAlreadyRegisteredError(
                "Email already registered"
            ) from error

        except Exception:
            await self.session.rollback()
            raise
        return user

    async def authenticate(self, data: UserLogin) -> UsersOrm:
        user = await self.users_repo.get_by_email(str(data.email))

        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if not self.verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        return user

    async def change_password(self, user_id: int, data: PasswordChange) -> None:
        user = await self.users_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        if not self.verify_password(data.old_password, user.password_hash):
            raise InvalidOldPasswordError("Invalid old password")

        password_data = PasswordHashUpdate(
            password_hash=self.hash_password(data.new_password),
        )

        try:
            await self.users_repo.update_password_hash(
                data=password_data,
                user_id=user_id,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise