from fastapi import APIRouter
from app.api.routes.v1.account import endpoints
from .response import AccountResponse, AccountsListResponse, AccountDeleteResponse, ErrorResponse

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Create account
router.add_api_route(
    path="",
    endpoint=endpoints.create_account,
    methods=["POST"],
    summary="Create a new account",
    description="Create a new account in the system",
    response_model=AccountResponse,
    status_code=201,
)

# List accounts
router.add_api_route(
    path="",
    endpoint=endpoints.list_accounts,
    methods=["GET"],
    summary="List accounts",
    description="Get a paginated list of accounts, optionally filtered by subscription status or plan",
    response_model=AccountsListResponse,
)

# Get account by ID
router.add_api_route(
    path="/{account_id}",
    endpoint=endpoints.get_account,
    methods=["GET"],
    summary="Get account by ID",
    description="Retrieve a specific account by its ID",
    response_model=AccountResponse,
)

# Update account
router.add_api_route(
    path="/{account_id}",
    endpoint=endpoints.update_account,
    methods=["PATCH"],
    summary="Update account",
    description="Update an existing account's information",
    response_model=AccountResponse,
)

# Update account plan
router.add_api_route(
    path="/{account_id}/plan",
    endpoint=endpoints.update_account_plan,
    methods=["PATCH"],
    summary="Update account plan",
    description="Update an account's plan and subscription status",
    response_model=AccountResponse,
)

# Update feature flags
router.add_api_route(
    path="/{account_id}/features",
    endpoint=endpoints.update_feature_flags,
    methods=["PATCH"],
    summary="Update feature flags",
    description="Update an account's feature flags",
    response_model=AccountResponse,
)

# Update subscription status
router.add_api_route(
    path="/{account_id}/subscription",
    endpoint=endpoints.update_subscription_status,
    methods=["PATCH"],
    summary="Update subscription status",
    description="Update an account's subscription status",
    response_model=AccountResponse,
)