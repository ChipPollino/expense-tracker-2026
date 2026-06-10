from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.db import get_db
from src.models import UsersOrm
from src.schemas.analytics import (
    AnalyticsPeriod,
    AnalyticsSummary,
    CategoryExpenseStats,
    MonthlyExpenseStats,
)
from src.services.analytics import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
)
async def get_summary(
    period: AnalyticsPeriod = Depends(),
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.get_summary(
        user_id=current_user.id,
        period=period,
    )


@router.get(
    "/by-category",
    response_model=list[CategoryExpenseStats],
)
async def get_by_category(
    period: AnalyticsPeriod = Depends(),
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.get_by_category(
        user_id=current_user.id,
        period=period,
    )


@router.get(
    "/monthly",
    response_model=list[MonthlyExpenseStats],
)
async def get_monthly(
    period: AnalyticsPeriod = Depends(),
    current_user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.get_monthly(
        user_id=current_user.id,
        period=period,
    )