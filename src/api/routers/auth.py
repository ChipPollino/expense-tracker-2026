from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.users import (
    PasswordChange,
    UserCreate,
    UserLogin,
    UserRead,
)
from src.services.auth import AuthService
from src.services.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    UserNotFoundError,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.register(data)

    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.post("/login")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        user = await service.authenticate(data)

    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

    request.session["user_id"] = user.id

    return {
        "message": "Logged in successfully",
    }


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logged out successfully",
    }


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    current_user: UsersOrm = Depends(get_current_user),
):
    return current_user


@router.patch("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        await service.change_password(
            user_id=current_user.id,
            data=data,
        )

    except InvalidOldPasswordError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    return {
        "message": "Password changed successfully",
    }