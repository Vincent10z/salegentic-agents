from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)