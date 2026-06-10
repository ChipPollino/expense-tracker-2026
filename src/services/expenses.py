from sqlalchemy.ext.asyncio import AsyncSession

from src.models.expenses import ExpensesOrm
from src.repositories.categories import CategoriesRepository
from src.repositories.expenses import ExpensesRepository
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


class ExpensesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expenses_repo = ExpensesRepository(session)
        self.categories_repo = CategoriesRepository(session)

    @staticmethod
    def to_expense_read(expense: ExpensesOrm) -> ExpenseRead:
        return ExpenseRead(
            id=expense.id,
            category=expense.category.name,
            amount=expense.amount,
            expense_date=expense.expense_date,
            description=expense.description,
        )

    async def get_by_id(
        self,
        expense_id: int,
        user_id: int,
    ) -> ExpenseRead:
        expense = await self.expenses_repo.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )

        if expense is None:
            raise ExpenseNotFoundError("Expense not found")

        return self.to_expense_read(expense)

    async def get_all(
        self,
        user_id: int,
        filters: ExpenseFilter | None = None,
    ) -> list[ExpenseRead]:
        if filters is None:
            filters = ExpenseFilter()

        expenses = await self.expenses_repo.get_filtered_by_user(
            user_id=user_id,
            filter_by=filters,
        )

        return [
            self.to_expense_read(expense)
            for expense in expenses
        ]

    async def create(
        self,
        data: ExpenseCreate,
        user_id: int,
    ) -> ExpenseRead:
        category = await self.categories_repo.get_by_id_for_user(
            category_id=data.category_id,
            user_id=user_id,
        )

        if category is None:
            raise CategoryNotFoundError("Category not found")

        try:
            created_expense = await self.expenses_repo.add(
                data=data,
                user_id=user_id,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        expense = await self.expenses_repo.get_by_id_for_user(
            expense_id=created_expense.id,
            user_id=user_id,
        )

        if expense is None:
            raise ExpenseNotFoundError("Expense not found")

        return self.to_expense_read(expense)

    async def update(
        self,
        data: ExpenseUpdate,
        expense_id: int,
        user_id: int,
    ) -> ExpenseRead:
        values = data.model_dump(exclude_unset=True)

        if not values:
            raise EmptyUpdateError("No fields to update")

        expense = await self.expenses_repo.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )

        if expense is None:
            raise ExpenseNotFoundError("Expense not found")

        if data.category_id is not None:
            category = await self.categories_repo.get_by_id_for_user(
                category_id=data.category_id,
                user_id=user_id,
            )

            if category is None:
                raise CategoryNotFoundError("Category not found")

        try:
            await self.expenses_repo.update_by_id_for_user(
                data=data,
                expense_id=expense_id,
                user_id=user_id,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        updated_expense = await self.expenses_repo.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )

        if updated_expense is None:
            raise ExpenseNotFoundError("Expense not found")

        return self.to_expense_read(updated_expense)

    async def delete(
        self,
        expense_id: int,
        user_id: int,
    ) -> None:
        expense = await self.expenses_repo.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )

        if expense is None:
            raise ExpenseNotFoundError("Expense not found")

        try:
            await self.expenses_repo.delete_by_id_for_user(
                expense_id=expense_id,
                user_id=user_id,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise