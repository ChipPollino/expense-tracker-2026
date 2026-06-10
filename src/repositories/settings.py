from src.models import SettingsOrm
from src.repositories.base import BaseRepository
from src.schemas.settings import SettingsUpdate


class SettingsRepository(BaseRepository):
    model = SettingsOrm

    async def get_by_user_id(self, user_id: int):
        return await self.get_one_or_none(user_id=user_id)

    async def update_by_user_id(self, data: SettingsUpdate, user_id: int) -> None:
        await self.edit(data=data,
                        is_patch=True,
                        user_id=user_id)