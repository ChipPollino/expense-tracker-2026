from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import UsersOrm
from src.repositories.base import BaseRepository
from src.schemas.users import PasswordHashUpdate


class UsersRepository(BaseRepository):
    model = UsersOrm

    async def get_by_id(self, user_id: int):
        return await self.get_one_or_none(id=user_id)

    async def get_by_email(self, email: str):
        return await self.get_one_or_none(email=email)

    async def get_by_id_with_settings(self, user_id: int):
        stmt = (select(UsersOrm)
                .options(selectinload(UsersOrm.settings))
                .filter_by(id=user_id))
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def change_password_hash(self, data: PasswordHashUpdate, user_id: int) -> None:
        await self.edit(data, is_patch=True, id=user_id)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user is not None:
            await self.session.delete(user)
        # не через обычный delete
        # тк await self.session.delete(user) работает с ORM и cascade работает надежнее