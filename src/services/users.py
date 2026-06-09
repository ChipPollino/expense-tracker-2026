from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UsersOrm
from src.repositories.users import UsersRepository
from src.schemas.users import UserUpdate

from src.services.exceptions import (
    EmailAlreadyRegisteredError,
    EmptyUpdateError,
    UserNotFoundError,
)


class UsersService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_repo = UsersRepository(session)

    async def get_profile(self, user_id: int) -> UsersOrm:
        user = await self.users_repo.get_by_id_with_settings(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        return user

    async def update_profile(
        self,
        user_id: int,
        data: UserUpdate,
    ) -> UsersOrm:
        values = data.model_dump(exclude_unset=True)

        if not values:
            raise EmptyUpdateError("No fields to update")

        user = await self.users_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        if "email" in data.model_fields_set:
            existing_user = await self.users_repo.get_by_email(
                str(data.email)
            )

            if existing_user is not None and existing_user.id != user_id:
                raise EmailAlreadyRegisteredError(
                    "Email already registered"
                )

        try:
            await self.users_repo.update_by_id(
                data=data,
                user_id=user_id,
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

        updated_user = await self.users_repo.get_by_id(user_id)

        if updated_user is None:
            raise UserNotFoundError("User not found")

        return updated_user

    async def delete_profile(self, user_id: int) -> None:
        user = await self.users_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        try:
            await self.users_repo.delete_by_id(user_id)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise