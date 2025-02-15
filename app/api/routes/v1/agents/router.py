from fastapi import APIRouter

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)