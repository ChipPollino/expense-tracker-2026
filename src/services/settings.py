from sqlalchemy.ext.asyncio import AsyncSession

from src.models import SettingsOrm
from src.repositories.settings import SettingsRepository
from src.schemas.settings import SettingsUpdate
from src.services.exceptions import (
    EmptyUpdateError,
    SettingsNotFoundError,
)


class SettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings_repo = SettingsRepository(session)

    async def get_settings(self, user_id: int) -> SettingsOrm:
        settings = await self.settings_repo.get_by_user_id(user_id)

        if settings is None:
            raise SettingsNotFoundError("Settings not found")
        return settings

    async def update_settings(self, user_id: int, data: SettingsUpdate) -> SettingsOrm:
        values = data.model_dump(exclude_unset=True)

        if not values:
            raise EmptyUpdateError("No fields to update")

        settings = await self.settings_repo.get_by_user_id(user_id)

        if settings is None:
            raise SettingsNotFoundError("Settings not found")

        try:
            await self.settings_repo.update_by_user_id(data=data, user_id=user_id)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        updated_settings = await self.settings_repo.get_by_user_id(user_id)

        if updated_settings is None:
            raise SettingsNotFoundError("Settings not found")

        return updated_settings