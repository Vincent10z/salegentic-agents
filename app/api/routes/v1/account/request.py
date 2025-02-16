from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    PENDING = "pending"


class CreateAccountRequest(BaseModel):
    """Request model for creating a new account"""
    name: str
    active_plan_id: Optional[str] = None
    subscription_status: Optional[SubscriptionStatus] = None
    warmup_enabled: bool = True
    products_enabled: bool = True


class UpdateAccountRequest(BaseModel):
    """Request model for updating an existing account"""
    name: Optional[str] = None
    warmup_enabled: Optional[bool] = None
    products_enabled: Optional[bool] = None
    subscription_status: Optional[SubscriptionStatus] = None


class UpdateAccountPlanRequest(BaseModel):
    """Request model for updating account plan"""
    plan_id: str
    subscription_status: Optional[SubscriptionStatus] = None


class UpdateFeatureFlagsRequest(BaseModel):
    """Request model for updating account feature flags"""
    warmup_enabled: Optional[bool] = None
    products_enabled: Optional[bool] = None


class UpdateSubscriptionStatusRequest(BaseModel):
    """Request model for updating subscription status"""
    status: SubscriptionStatus