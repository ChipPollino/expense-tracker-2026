from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.expenses import (
    ExpenseCreate,
    ExpenseFilter,
    ExpenseRead,
    ExpenseUpdate,
)
from src.services.exceptions import (
    CategoryNotFoundError,
    EmptyUpdateError,
    ExpenseNotFoundError,
)
from src.services.expenses import ExpensesService


router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.get(
    "",
    response_model=list[ExpenseRead],
)
async def get_expenses(
    filters: ExpenseFilter = Depends(),
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpensesService(db)

    return await service.get_all(
        user_id=current_user.id,
        filters=filters,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseRead,
)
async def get_expense(
    expense_id: int,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpensesService(db)

    try:
        return await service.get_by_id(
            expense_id=expense_id,
            user_id=current_user.id,
        )

    except ExpenseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    data: ExpenseCreate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpensesService(db)

    try:
        return await service.create(
            data=data,
            user_id=current_user.id,
        )

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/{expense_id}",
    response_model=ExpenseRead,
)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpensesService(db)

    try:
        return await service.update(
            data=data,
            expense_id=expense_id,
            user_id=current_user.id,
        )

    except ExpenseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except EmptyUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense(
    expense_id: int,
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpensesService(db)

    try:
        await service.delete(
            expense_id=expense_id,
            user_id=current_user.id,
        )

    except ExpenseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)