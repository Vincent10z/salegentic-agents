from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class WorkspaceResponse(BaseModel):
    """Response model for workspace data"""
    id: str
    name: str
    slug: Optional[str] = None
    account_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def transform_workspace_response(workspace) -> WorkspaceResponse:
    """Transform a Workspace model instance into a WorkspaceResponse."""
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        account_id=workspace.account_id,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        deleted_at=workspace.deleted_at
    )


class WorkspacesListResponse(BaseModel):
    """Response model for listing multiple workspaces"""
    items: List[WorkspaceResponse]
    total: int = Field(description="Total number of workspaces")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")

    class Config:
        from_attributes = True


class WorkspaceDeleteResponse(BaseModel):
    """Response model for workspace deletion"""
    message: str = "Workspace successfully deleted"
    workspace_id: str


def transform_workspaces_list_response(
        workspaces: List,
        total: int,
        page: int,
        size: int
) -> WorkspacesListResponse:
    """Transform a list of Workspace models into a WorkspacesListResponse."""
    return WorkspacesListResponse(
        items=[transform_workspace_response(workspace) for workspace in workspaces],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size  # Calculate total pages
    )


def transform_workspace_delete_response(workspace_id: str) -> WorkspaceDeleteResponse:
    """Create a WorkspaceDeleteResponse for a deleted workspace."""
    return WorkspaceDeleteResponse(
        message="Workspace successfully deleted",
        workspace_id=workspace_id
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None
    context: Optional[dict] = None
