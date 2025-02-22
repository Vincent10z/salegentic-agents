from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from app.core.auth import get_current_user
from app.services.account.account_service import AccountService
from app.core.dependencies.services import get_account_service

from .request import (
    CreateAccountRequest,
    UpdateAccountRequest,
    UpdateAccountPlanRequest,
    UpdateFeatureFlagsRequest,
    UpdateSubscriptionStatusRequest,
    SubscriptionStatus
)
from .response import (
    AccountResponse,
    AccountsListResponse,
    AccountDeleteResponse
)
from ..account.response import (
    new_account_response,
    get_accounts_response,
    account_delete_response
)

router = APIRouter()


async def create_account(
        request: CreateAccountRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Create a new account."""
    print("Received request data:", request.model_dump())  # Debugging step
    account = await account_service.create_account(**request.model_dump())
    return new_account_response(account)


async def list_accounts(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        subscription_status: Optional[SubscriptionStatus] = None,
        plan_id: Optional[str] = None,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountsListResponse:
    """Get list of accounts with optional filtering."""
    if subscription_status:
        accounts = await account_service.get_accounts_by_subscription_status(subscription_status)
        total = len(accounts)  # You might want to get this from the service
    elif plan_id:
        accounts = await account_service.get_accounts_by_plan(plan_id)
        total = len(accounts)  # You might want to get this from the service
    else:
        accounts = await account_service.get_accounts(page=page, size=size)
        total = len(accounts)  # You might want to get this from the service

    return get_accounts_response(accounts, total, page, size)


async def get_account(
        account_id: str,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Get account by ID."""
    account = await account_service.get_account(account_id)
    return new_account_response(account)


async def update_account(
        account_id: str,
        request: UpdateAccountRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Update account information."""
    account = await account_service.update_account(
        account_id,
        request.model_dump(exclude_unset=True)
    )
    return new_account_response(account)


async def update_account_plan(
        account_id: str,
        request: UpdateAccountPlanRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Update account's plans."""
    account = await account_service.update_plan(
        account_id,
        request.plan_id,
        request.subscription_status
    )
    return new_account_response(account)


async def update_feature_flags(
        account_id: str,
        request: UpdateFeatureFlagsRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Update account's feature flags."""
    account = await account_service.update_feature_flags(
        account_id,
        request.products_enabled
    )
    return new_account_response(account)


async def update_subscription_status(
        account_id: str,
        request: UpdateSubscriptionStatusRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends(get_account_service)
) -> AccountResponse:
    """Update account's subscription status."""
    account = await account_service.update_subscription_status(
        account_id,
        request.status
    )
    return new_account_response(account)
