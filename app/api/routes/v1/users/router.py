from fastapi import APIRouter
from app.api.routes.v1.users import endpoints
from .response import UserResponse, UsersListResponse, UserDeleteResponse, ErrorResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Create user
router.add_api_route(
    path="",
    endpoint=endpoints.create_user,
    methods=["POST"],
    summary="Create a new user",
    description="Create a new user in the system",
    response_model=UserResponse,
    status_code=201,
)

# List users
router.add_api_route(
    path="",
    endpoint=endpoints.list_users,
    methods=["GET"],
    summary="List users",
    description="Get a paginated list of users, optionally filtered by account",
    response_model=UsersListResponse,
)

# Get user by ID
router.add_api_route(
    path="/{user_id}",
    endpoint=endpoints.get_user,
    methods=["GET"],
    summary="Get user by ID",
    description="Retrieve a specific user by their ID",
    response_model=UserResponse,
)

# Update user
router.add_api_route(
    path="/{user_id}",
    endpoint=endpoints.update_user,
    methods=["PATCH"],
    summary="Update user",
    description="Update an existing user's information",
    response_model=UserResponse,
)

# Update user role
router.add_api_route(
    path="/{user_id}/role",
    endpoint=endpoints.update_user_role,
    methods=["PATCH"],
    summary="Update user role",
    description="Update a user's role in the system",
    response_model=UserResponse,
)

# Update user account
router.add_api_route(
    path="/{user_id}/account",
    endpoint=endpoints.update_user_account,
    methods=["PATCH"],
    summary="Update user account",
    description="Update a user's associated account",
    response_model=UserResponse,
)

# Get user by email
router.add_api_route(
    path="/email/{email}",
    endpoint=endpoints.get_user_by_email,
    methods=["GET"],
    summary="Get user by email",
    description="Retrieve a specific user by their email address",
    response_model=UserResponse,
)

# Delete user
router.add_api_route(
    path="/{user_id}",
    endpoint=endpoints.delete_user,
    methods=["DELETE"],
    summary="Delete user",
    description="Delete a user from the system",
    response_model=UserDeleteResponse,
)