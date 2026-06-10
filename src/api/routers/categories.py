from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.categories import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from src.services.categories import CategoriesService
from src.services.exceptions import (
    CategoryAlreadyExistsError,
    CategoryHasExpensesError,
    CategoryNotFoundError,
)


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get(
    "",
    response_model=list[CategoryRead],
)
async def get_categories(
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoriesService(db)

    return await service.get_all(
        user_id=current_user.id,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
)
async def get_category(
    category_id: int,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoriesService(db)

    try:
        return await service.get_by_id(
            category_id=category_id,
            user_id=current_user.id,
        )

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoriesService(db)

    try:
        return await service.create(
            data=data,
            user_id=current_user.id,
        )

    except CategoryAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoriesService(db)

    try:
        return await service.update_name(
            data=data,
            category_id=category_id,
            user_id=current_user.id,
        )

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except CategoryAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoriesService(db)

    try:
        await service.delete(
            category_id=category_id,
            user_id=current_user.id,
        )

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except CategoryHasExpensesError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)