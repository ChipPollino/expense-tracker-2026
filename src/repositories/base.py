from sqlalchemy import select, insert, delete, update
from pydantic import BaseModel


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = (select(self.model)
                 .filter_by(**filter_by))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseModel, **extra_values):
        values = data.model_dump()
        values.update(extra_values)

        add_stmt = (insert(self.model)
                    .values(**values)
                    .returning(self.model)) # или self.model.id
        result = await self.session.execute(add_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseModel, is_patch: bool = True, **filter_by) -> None:
        if not filter_by:
            raise ValueError("Edit requires at least one filter")

        update_stmt = (update(self.model)
                       .filter_by(**filter_by)
                       .values(**data.model_dump(exclude_unset=is_patch)))
        # exclude_unset не принимает во внимание непереданные значения
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        if not filter_by:
            raise ValueError("Delete requires at least one filter")

        delete_stmt = (delete(self.model)
                       .filter_by(**filter_by))
        await self.session.execute(delete_stmt)