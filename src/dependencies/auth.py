from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.db import get_db
from src.models import UsersOrm
from src.repositories.users import UsersRepository


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UsersOrm:
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    users_repo = UsersRepository(db)
    user = await users_repo.get_by_id(user_id)

    if user is None:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    return user