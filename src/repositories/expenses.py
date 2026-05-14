from sqlalchemy.orm import selectinload

from src.models import CategoriesOrm
from src.models.expenses import ExpensesOrm
from src.schemas.expenses import ExpenseFilter, ExpenseOrderBy

from src.repositories.base import BaseRepository

from sqlalchemy import select


class ExpensesRepository(BaseRepository):
    model = ExpensesOrm

    async def get_all_by_user(self, user_id: int):
        return await self.get_filtered_by_user(user_id=user_id, filter_by=ExpenseFilter())

    async def get_filtered_by_user(self, user_id: int, filter_by: ExpenseFilter):
        stmt = (select(ExpensesOrm)
                .options(selectinload(ExpensesOrm.category))
                .filter_by(user_id=user_id))

        if filter_by.category_id is not None:
            stmt = stmt.where(ExpensesOrm.category_id == filter_by.category_id)

        if filter_by.date_from is not None:
            stmt = stmt.where(ExpensesOrm.expense_date >= filter_by.date_from)

        if filter_by.date_to is not None:
            stmt = stmt.where(ExpensesOrm.expense_date <= filter_by.date_to)

        if filter_by.amount_from is not None:
            stmt = stmt.where(ExpensesOrm.amount >= filter_by.amount_from)

        if filter_by.amount_to is not None:
            stmt = stmt.where(ExpensesOrm.amount <= filter_by.amount_to)

        if filter_by.order_by == ExpenseOrderBy.NEWEST:
            stmt = stmt.order_by(ExpensesOrm.expense_date.desc())

        elif filter_by.order_by == ExpenseOrderBy.OLDEST:
            stmt = stmt.order_by(ExpensesOrm.expense_date.asc())

        elif filter_by.order_by == ExpenseOrderBy.AMOUNT_ASC:
            stmt = stmt.order_by(ExpensesOrm.amount.asc())

        elif filter_by.order_by == ExpenseOrderBy.AMOUNT_DESC:
            stmt = stmt.order_by(ExpensesOrm.amount.desc())

        elif filter_by.order_by == ExpenseOrderBy.CATEGORY_ASC:
            stmt = (stmt
                    .join(ExpensesOrm.category)
                    .order_by(CategoriesOrm.name.asc(), ExpensesOrm.expense_date.desc()))

        elif filter_by.order_by == ExpenseOrderBy.CATEGORY_DESC:
            stmt = (stmt
                    .join(ExpensesOrm.category)
                    .order_by(CategoriesOrm.name.desc(), ExpensesOrm.expense_date.desc()))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id_for_user(self, expense_id: int, user_id: int):
        stmt = (select(ExpensesOrm)
                .options(selectinload(ExpensesOrm.category))
                .filter_by(id=expense_id, user_id=user_id))
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def delete_by_id_for_user(self, expense_id: int, user_id: int) -> None:
        await self.delete(id=expense_id, user_id=user_id)