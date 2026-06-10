import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.api.routers.auth import router as auth_router
from src.api.routers.categories import router as categories_router
from src.api.routers.expenses import router as expenses_router
from src.api.routers.settings import router as settings_router
from src.api.routers.users import router as users_router
from src.api.routers.analytics import router as analytics_router
from src.core.config import settings

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from src.api.routers.pages import router as pages_router


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=False,
)

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(expenses_router)
app.include_router(settings_router)
app.include_router(users_router)
app.include_router(analytics_router)
app.include_router(pages_router)


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)