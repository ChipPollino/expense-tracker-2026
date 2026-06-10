from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.users import UserRead, UserUpdate
from src.services.exceptions import (
    EmailAlreadyRegisteredError,
    EmptyUpdateError,
    UserNotFoundError,
)
from src.services.users import UsersService


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_profile(
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UsersService(db)

    try:
        return await service.get_profile(
            user_id=current_user.id,
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/me",
    response_model=UserRead,
)
async def update_profile(
    data: UserUpdate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UsersService(db)

    try:
        return await service.update_profile(
            user_id=current_user.id,
            data=data,
        )

    except EmptyUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(
    request: Request,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UsersService(db)

    try:
        await service.delete_profile(
            user_id=current_user.id,
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    request.session.clear()

    return Response(status_code=status.HTTP_204_NO_CONTENT)