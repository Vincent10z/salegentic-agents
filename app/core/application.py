# app/core/application.py
from fastapi import FastAPI
from app.core.config import Settings
from app.api.routes.v1.router import router as api_v1_router
from app.core.middleware.error_handler import ErrorHandlerMiddleware


def create_app() -> FastAPI:
    settings = Settings()

    app = FastAPI(
        title="Salesgentic Agents",
        description=settings.PROJECT_DESCRIPTION,
        version="v0.0.1",
        # openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(ErrorHandlerMiddleware)

    # Include main v1 router
    app.include_router(api_v1_router, prefix="/v1")

    return app
