from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.settings import SettingsRead, SettingsUpdate
from src.services.exceptions import (
    EmptyUpdateError,
    SettingsNotFoundError,
)
from src.services.settings import SettingsService


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


@router.get(
    "",
    response_model=SettingsRead,
)
async def get_settings(
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)

    try:
        return await service.get_settings(
            user_id=current_user.id,
        )

    except SettingsNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "",
    response_model=SettingsRead,
)
async def update_settings(
    data: SettingsUpdate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)

    try:
        return await service.update_settings(
            user_id=current_user.id,
            data=data,
        )

    except EmptyUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except SettingsNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )