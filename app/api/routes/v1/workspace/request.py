from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateWorkspaceRequest(BaseModel):
    """Request model for creating a new workspace"""
    name: str
    account_id: str


class UpdateWorkspaceRequest(BaseModel):
    """Request model for updating an existing workspace"""
    name: Optional[str] = None
    slug: Optional[str] = None