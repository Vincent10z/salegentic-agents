from fastapi import APIRouter

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)