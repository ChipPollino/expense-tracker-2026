from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CategoriesOrm
from src.repositories.categories import CategoriesRepository
from src.repositories.expenses import ExpensesRepository
from src.schemas.categories import CategoryCreate, CategoryUpdate
from src.services.exceptions import (
    CategoryAlreadyExistsError,
    CategoryHasExpensesError,
    CategoryNotFoundError,
)


class CategoriesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.categories_repo = CategoriesRepository(session)
        self.expenses_repo = ExpensesRepository(session)

    async def get_all(self, user_id: int) -> list[CategoriesOrm]:
        return await self.categories_repo.get_all_by_user(user_id)

    async def get_by_id(self, category_id: int, user_id: int) -> CategoriesOrm:
        category = await self.categories_repo.get_by_id_for_user(
            category_id=category_id,
            user_id=user_id,
        )

        if category is None:
            raise CategoryNotFoundError("Category not found")
        return category

    async def create(self, data: CategoryCreate, user_id: int) -> CategoriesOrm:
        existing_category = await self.categories_repo.get_by_name_for_user(
            category_name=data.name,
            user_id=user_id,
        )

        if existing_category is not None:
            raise CategoryAlreadyExistsError(
                "Category already exists"
            )

        try:
            category = await self.categories_repo.add(
                data=data,
                user_id=user_id,
            )

            await self.session.commit()

        except IntegrityError as error:
            await self.session.rollback()
            raise CategoryAlreadyExistsError(
                "Category already exists"
            ) from error

        except Exception:
            await self.session.rollback()
            raise

        return category

    async def update_name(self, data: CategoryUpdate, category_id: int, user_id: int) -> CategoriesOrm:
        category = await self.get_by_id(
            category_id=category_id,
            user_id=user_id,
        )

        existing_category = await self.categories_repo.get_by_name_for_user(
            category_name=data.name,
            user_id=user_id,
        )

        if (
            existing_category is not None
            and existing_category.id != category_id
        ):
            raise CategoryAlreadyExistsError(
                "Category already exists"
            )

        if category.name == data.name:
            return category

        try:
            await self.categories_repo.update_name(
                data=data,
                category_id=category_id,
                user_id=user_id,
            )

            await self.session.commit()

        except IntegrityError as error:
            await self.session.rollback()
            raise CategoryAlreadyExistsError(
                "Category already exists"
            ) from error

        except Exception:
            await self.session.rollback()
            raise

        updated_category = await self.get_by_id(
            category_id=category_id,
            user_id=user_id,
        )

        return updated_category

    async def delete(
        self,
        category_id: int,
        user_id: int,
    ) -> None:
        await self.get_by_id(
            category_id=category_id,
            user_id=user_id,
        )

        has_expenses = await self.expenses_repo.has_expenses_in_category(
            category_id=category_id,
            user_id=user_id,
        )

        if has_expenses:
            raise CategoryHasExpensesError(
                "Cannot delete category with expenses"
            )

        try:
            await self.categories_repo.delete_by_id_for_user(
                category_id=category_id,
                user_id=user_id,
            )

            await self.session.commit()

        except IntegrityError as error:
            await self.session.rollback()
            raise CategoryHasExpensesError(
                "Cannot delete category with expenses"
            ) from error

        except Exception:
            await self.session.rollback()
            raise