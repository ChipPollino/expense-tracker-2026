from src.models import CategoriesOrm
from src.repositories.base import BaseRepository
from src.schemas.categories import CategoryUpdate


class CategoriesRepository(BaseRepository):
    model = CategoriesOrm

    async def get_all_by_user(self, user_id: int):
        return await self.get_all(user_id=user_id)

    async def get_by_id_for_user(self, category_id: int, user_id: int):
        return await self.get_one_or_none(id=category_id,
                                          user_id=user_id)

    async def get_by_name_for_user(self, category_name: str, user_id: int):
        return await self.get_one_or_none(name=category_name,
                                          user_id=user_id)

    async def change_name(self, data: CategoryUpdate, category_id: int, user_id: int) -> None:
        await self.edit(data=data,
                        is_patch=True,
                        id=category_id,
                        user_id=user_id)

    async def delete_by_id_for_user(self, category_id: int, user_id: int) -> None:
        await self.delete(id=category_id,
                          user_id=user_id)