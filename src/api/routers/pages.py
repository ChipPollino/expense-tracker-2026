from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
async def index(request: Request):
    if request.session.get("user_id") is None:
        return RedirectResponse(url="/login", status_code=303)

    return RedirectResponse(url="/app", status_code=303)


@router.get("/login", include_in_schema=False)
async def login_page(request: Request):
    if request.session.get("user_id") is not None:
        return RedirectResponse(url="/app", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"page_title": "Вход"},
    )


@router.get("/register", include_in_schema=False)
async def register_page(request: Request):
    if request.session.get("user_id") is not None:
        return RedirectResponse(url="/app", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"page_title": "Регистрация"},
    )


@router.get("/app", include_in_schema=False)
async def app_page(request: Request):
    if request.session.get("user_id") is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={"page_title": "Expense Tracker"},
    )
