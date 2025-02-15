# app/routes/v1/health/router.py
from fastapi import APIRouter
from . import endpoints

router = APIRouter(
    prefix="/health",
    tags=["Health of app"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)

# Health Route
router.add_api_route(
    path="/",
    endpoint=endpoints.health_check,
    methods=["GET"],
    summary="Health Check",
    description="Check if the application is healthy",
    response_model=dict
)