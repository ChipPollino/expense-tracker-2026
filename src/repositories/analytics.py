from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import CategoriesOrm
from src.models.expenses import ExpensesOrm


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def apply_period_filters(
        stmt,
        date_from: datetime | None,
        date_to: datetime | None,
    ):
        if date_from is not None:
            stmt = stmt.where(
                ExpensesOrm.expense_date >= date_from
            )

        if date_to is not None:
            stmt = stmt.where(
                ExpensesOrm.expense_date <= date_to
            )

        return stmt

    async def get_summary(
        self,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        stmt = (
            select(
                func.coalesce(
                    func.sum(ExpensesOrm.amount),
                    0,
                ).label("total"),
                func.count(ExpensesOrm.id).label("expenses_count"),
            )
            .where(ExpensesOrm.user_id == user_id)
        )

        stmt = self.apply_period_filters(
            stmt=stmt,
            date_from=date_from,
            date_to=date_to,
        )

        result = await self.session.execute(stmt)

        return result.mappings().one()

    async def get_by_category(
        self,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        stmt = (
            select(
                CategoriesOrm.id.label("category_id"),
                CategoriesOrm.name.label("category"),
                func.sum(ExpensesOrm.amount).label("total"),
            )
            .join(
                ExpensesOrm,
                ExpensesOrm.category_id == CategoriesOrm.id,
            )
            .where(
                ExpensesOrm.user_id == user_id,
                CategoriesOrm.user_id == user_id,
            )
            .group_by(
                CategoriesOrm.id,
                CategoriesOrm.name,
            )
            .order_by(
                func.sum(ExpensesOrm.amount).desc()
            )
        )

        stmt = self.apply_period_filters(
            stmt=stmt,
            date_from=date_from,
            date_to=date_to,
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()

    async def get_monthly(
        self,
        user_id: int,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        month = func.date_trunc(
            "month",
            ExpensesOrm.expense_date,
        ).label("month")

        stmt = (
            select(
                month,
                func.sum(ExpensesOrm.amount).label("total"),
            )
            .where(ExpensesOrm.user_id == user_id)
            .group_by(month)
            .order_by(month.asc())
        )

        stmt = self.apply_period_filters(
            stmt=stmt,
            date_from=date_from,
            date_to=date_to,
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()