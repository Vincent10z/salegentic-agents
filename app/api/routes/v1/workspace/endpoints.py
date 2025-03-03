from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.services.workspace.workspace_service import WorkspaceService
from app.core.dependencies.services import get_workspace_service
from .request import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
)
from .response import (
    WorkspaceResponse,
    WorkspacesListResponse,
    WorkspaceDeleteResponse,
    ErrorResponse,
    transform_workspace_response,
    transform_workspaces_list_response,
    transform_workspace_delete_response
)

router = APIRouter()


async def create_workspace(
        request: CreateWorkspaceRequest,
        workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceResponse:
    """Create a new workspace."""
    workspace = await workspace_service.create_workspace(request)
    return workspace


async def get_workspace(
        workspace_id: str,
        workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceResponse:
    """Get a specific workspace."""
    return await workspace_service.get_workspace(workspace_id)


async def list_workspaces(
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1, le=1000),
        account_id: Optional[str] = None,
        workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspacesListResponse:
    """Get list of workspaces."""
    return await workspace_service.get_workspaces(page, size, account_id)


async def update_workspace(
        workspace_id: str,
        request: UpdateWorkspaceRequest,
        workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceResponse:
    """Update a workspace."""
    return await workspace_service.update_workspace(workspace_id, request)


async def delete_workspace(
        workspace_id: str,
        workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceDeleteResponse:
    """Delete a workspace."""
    await workspace_service.delete_workspace(workspace_id)
    return transform_workspace_delete_response(workspace_id)