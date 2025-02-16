from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from app.core.auth import get_current_user
from app.services.account.account import AccountService
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


@router.post("", response_model=AccountResponse)
async def create_account(
        request: CreateAccountRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Create a new account."""
    account = await account_service.create_account(**request.model_dump())
    return new_account_response(account)


@router.get("", response_model=AccountsListResponse)
async def list_accounts(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        subscription_status: Optional[SubscriptionStatus] = None,
        plan_id: Optional[str] = None,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
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


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
        account_id: str,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Get account by ID."""
    account = await account_service.get_account(account_id)
    return new_account_response(account)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
        account_id: str,
        request: UpdateAccountRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Update account information."""
    account = await account_service.update_account(
        account_id,
        request.model_dump(exclude_unset=True)
    )
    return new_account_response(account)


@router.patch("/{account_id}/plan", response_model=AccountResponse)
async def update_account_plan(
        account_id: str,
        request: UpdateAccountPlanRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Update account's plan."""
    account = await account_service.update_plan(
        account_id,
        request.plan_id,
        request.subscription_status
    )
    return new_account_response(account)


@router.patch("/{account_id}/features", response_model=AccountResponse)
async def update_feature_flags(
        account_id: str,
        request: UpdateFeatureFlagsRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Update account's feature flags."""
    account = await account_service.update_feature_flags(
        account_id,
        request.warmup_enabled,
        request.products_enabled
    )
    return new_account_response(account)


@router.patch("/{account_id}/subscription", response_model=AccountResponse)
async def update_subscription_status(
        account_id: str,
        request: UpdateSubscriptionStatusRequest,
        current_user: Dict = Depends(get_current_user),
        account_service: AccountService = Depends()
) -> AccountResponse:
    """Update account's subscription status."""
    account = await account_service.update_subscription_status(
        account_id,
        request.status
    )
    return new_account_response(account)