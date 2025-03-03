from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .request import SubscriptionStatus
from app.models.account import Account


class AccountResponse(BaseModel):
    """Response model for account data"""
    id: str
    name: str
    active_plan_id: Optional[str] = None
    products_enabled: bool
    subscription_status: Optional[SubscriptionStatus] = None
    plan_started_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountsListResponse(BaseModel):
    """Response model for listing multiple accounts"""
    items: List[AccountResponse]
    total: int = Field(description="Total number of accounts")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")

    class Config:
        from_attributes = True


class AccountDeleteResponse(BaseModel):
    """Response model for account deletion"""
    message: str = "Account successfully deleted"
    account_id: str


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None
    context: Optional[dict] = None


# Response modifications for all account requests
def new_account_response(account: Account) -> AccountResponse:
    """Transform an Account model instance into an AccountResponse."""
    return AccountResponse(
        id=account.id,
        name=account.name,
        active_plan_id=account.active_plan_id,
        products_enabled=account.products_enabled,
        subscription_status=account.subscription_status,
        plan_started_at=account.plan_started_at,
        created_at=account.created_at,
        updated_at=account.updated_at
    )


def get_accounts_response(
        accounts: List[Account],
        total: int,
        page: int,
        size: int
) -> AccountsListResponse:
    """Transform a list of Account models into an AccountsListResponse."""
    return AccountsListResponse(
        items=[new_account_response(account) for account in accounts],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size  # Calculate total pages
    )


def account_delete_response(account_id: str) -> AccountDeleteResponse:
    """Create an AccountDeleteResponse for a deleted account."""
    return AccountDeleteResponse(
        message="Account successfully deleted",
        account_id=account_id
    )
