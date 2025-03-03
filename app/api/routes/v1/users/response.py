from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .request import AccountRole, UserSource
from app.models.user import User


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    account_id: Optional[str] = None
    phone: Optional[str] = None
    where_found_us: Optional[str] = None
    account_role: AccountRole
    source: UserSource
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsersListResponse(BaseModel):
    """Response model for listing multiple users"""
    items: List[UserResponse]
    total: int = Field(description="Total number of users")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")

    class Config:
        from_attributes = True


class UserDeleteResponse(BaseModel):
    """Response model for user deletion"""
    message: str = "User successfully deleted"
    user_id: str


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None
    context: Optional[dict] = None


# Response modifications for all user requests
def transform_user_response(user: User) -> UserResponse:
    """Transform a User model instance into a UserResponse."""
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        account_id=user.account_id,
        phone=user.phone,
        where_found_us=user.where_found_us,
        account_role=user.account_role,
        source=user.source,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


def transform_users_list_response(
        users: List[User],
        total: int,
        page: int,
        size: int
) -> UsersListResponse:
    """Transform a list of User models into a UsersListResponse."""
    return UsersListResponse(
        items=[transform_user_response(user) for user in users],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size  # Calculate total pages
    )


def transform_user_delete_response(user_id: str) -> UserDeleteResponse:
    """Create a UserDeleteResponse for a deleted user."""
    return UserDeleteResponse(
        message="User successfully deleted",
        user_id=user_id
    )