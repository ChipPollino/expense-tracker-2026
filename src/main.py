from fastapi import FastAPI
import uvicorn
from fastapi.openapi.docs import get_swagger_ui_html
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.routers.settings import router as router_settings
from src.api.routers.users import router as router_users
# from src.api.expenses import router as router_expenses
from src.api.routers.categories import router as router_category


app = FastAPI(docs_url=None)

app.include_router(router_settings)
app.include_router(router_users)
# app.include_router(router_expenses)
app.include_router(router_category)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)