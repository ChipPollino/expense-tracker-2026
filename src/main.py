import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.api.routers.auth import router as auth_router
from src.core.config import settings


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=False,
)

app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)