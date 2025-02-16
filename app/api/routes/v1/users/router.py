from fastapi import APIRouter

router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)

router.add_api_route(
    path="",
    endpoint=endpoints.create,
    methods=["POST"],
    summary="Create a new user",
    description="Create a new user",
    response_model=dict
)