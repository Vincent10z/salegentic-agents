from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from enum import Enum


class AccountRole(str, Enum):
    STANDARD = "standard"
    ADMIN = "admin"


class UserSource(str, Enum):
    WEBSITE = "website"
    MANUAL = "manual"
    HUBSPOT = "hubspot"


class CreateUserRequest(BaseModel):
    """Request model for creating a new user"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    account_id: Optional[str] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    where_found_us: Optional[str] = None
    account_role: AccountRole = AccountRole.STANDARD
    source: UserSource = UserSource.WEBSITE


class UpdateUserRequest(BaseModel):
    """Request model for updating an existing user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    where_found_us: Optional[str] = None
    account_role: Optional[AccountRole] = None
    account_id: Optional[str] = None


class UpdateUserRoleRequest(BaseModel):
    """Request model for updating a user's role"""
    role: AccountRole


class UpdateUserAccountRequest(BaseModel):
    """Request model for updating a user's account"""
    account_id: str