import asyncio

from src.core.database import engine, Base
from src.models import *


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы успешно созданы")


if __name__ == "__main__":
    asyncio.run(create_tables())