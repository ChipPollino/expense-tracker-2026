from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.analytics import AnalyticsRepository
from src.schemas.analytics import (
    AnalyticsPeriod,
    AnalyticsSummary,
    CategoryExpenseStats,
    MonthlyExpenseStats,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.analytics_repo = AnalyticsRepository(session)

    async def get_summary(
        self,
        user_id: int,
        period: AnalyticsPeriod,
    ) -> AnalyticsSummary:
        row = await self.analytics_repo.get_summary(
            user_id=user_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )

        return AnalyticsSummary(
            total=row["total"],
            expenses_count=row["expenses_count"],
        )

    async def get_by_category(
        self,
        user_id: int,
        period: AnalyticsPeriod,
    ) -> list[CategoryExpenseStats]:
        rows = await self.analytics_repo.get_by_category(
            user_id=user_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )

        return [
            CategoryExpenseStats(
                category_id=row["category_id"],
                category=row["category"],
                total=row["total"],
            )
            for row in rows
        ]

    async def get_monthly(
        self,
        user_id: int,
        period: AnalyticsPeriod,
    ) -> list[MonthlyExpenseStats]:
        rows = await self.analytics_repo.get_monthly(
            user_id=user_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )

        return [
            MonthlyExpenseStats(
                month=row["month"].strftime("%Y-%m"),
                total=row["total"],
            )
            for row in rows
        ]