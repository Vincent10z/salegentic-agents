from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from app.core.auth import get_current_user
from app.core.dependencies.services import UserService, get_user_service
from .request import (
    CreateUserRequest,
    UpdateUserRequest,
    UpdateUserRoleRequest,
    UpdateUserAccountRequest
)
from .response import (
    UserResponse,
    UsersListResponse,
    UserDeleteResponse,
    ErrorResponse
)
from ..users.response import (
    transform_user_response,
    transform_users_list_response,
    transform_user_delete_response
)

router = APIRouter()


@router.post("", response_model=UserResponse)
async def create_user(
        request: CreateUserRequest,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user."""
    user = await user_service.create_user(**request.model_dump())
    return transform_user_response(user)


@router.get("", response_model=UsersListResponse)
async def list_users(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        account_id: Optional[str] = None,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UsersListResponse:
    """Get list of users with optional filtering by account."""
    if account_id:
        users = await user_service.get_account_users(account_id)
        total = len(users)  # You might want to get this from the service
    else:
        users = await user_service.get_users(page=page, size=size)
        total = len(users)  # You might want to get this from the service

    return transform_users_list_response(users, total, page, size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: str,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    return transform_user_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: str,
        request: UpdateUserRequest,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update user information."""
    user = await user_service.update_user(
        user_id,
        request.model_dump(exclude_unset=True)
    )
    return transform_user_response(user)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
        user_id: str,
        request: UpdateUserRoleRequest,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update user's role."""
    user = await user_service.update_user_role(user_id, request.role)
    return transform_user_response(user)


@router.patch("/{user_id}/account", response_model=UserResponse)
async def update_user_account(
        user_id: str,
        request: UpdateUserAccountRequest,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update user's account."""
    user = await user_service.update_user_account(user_id, request.account_id)
    return transform_user_response(user)


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
        email: str,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by email address."""
    user = await user_service.get_user_by_email(email)
    return transform_user_response(user)


@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
        user_id: str,
        current_user: Dict = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserDeleteResponse:
    """Delete a user."""
    await user_service.delete_user(user_id)
    return transform_user_delete_response(user_id)