from fastapi import APIRouter
from app.api.routes.v1.health.router import router as health_router
from app.api.routes.v1.agents.router import router as agents_router
from app.api.routes.v1.analytics.router import router as analytics_router
from app.api.routes.v1.auth.router import router as auth_router
from app.api.routes.v1.integrations.hubspot.router import router as hubspot_router
from app.api.routes.v1.users.router import router as users_router

router = APIRouter()

# Include all v1 routers
router.include_router(health_router)
router.include_router(agents_router)
router.include_router(analytics_router)
router.include_router(auth_router)
router.include_router(hubspot_router)
router.include_router(users_router)