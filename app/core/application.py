from fastapi import FastAPI
from app.core.config import Settings
from app.api.routes.v1.health.router import router as health_router


def create_app() -> FastAPI:
    settings = Settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION
    )

    # Include routers
    app.include_router(health_router)

    return app
