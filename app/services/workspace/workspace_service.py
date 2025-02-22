import string
from random import random
from typing import Optional, Tuple
from uuid import uuid4
from fastapi import HTTPException

from app.repositories.workspace.workspace import WorkspaceRepository
from app.models.workspace import Workspace
from app.core.id_generator.id_generator import generate_workspace_id
from app.api.routes.v1.workspace.request import (CreateWorkspaceRequest, UpdateWorkspaceRequest)
from app.api.routes.v1.workspace.response import (
    WorkspaceResponse,
    WorkspacesListResponse,
    transform_workspace_response,
    transform_workspaces_list_response
)


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository):
        self.repository = repository

    async def create_workspace(self, data: CreateWorkspaceRequest) -> WorkspaceResponse:
        """Create a new workspace."""
        slug = data.name
        workspace = await self.get_workspace_by_slug(slug)

        while workspace:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            slug = f"{data.name}-{random_suffix}"
            workspace = await self.get_workspace_by_slug(slug)

        workspace = Workspace(
            id=generate_workspace_id(),
            name=data.name,
            slug=slug,
            account_id=data.account_id
        )

        created_workspace = await self.repository.create_workspace(workspace)
        return transform_workspace_response(created_workspace)

    async def get_workspace(self, workspace_id: str) -> WorkspaceResponse:
        """Get a workspace by ID."""
        workspace = await self.repository.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=404,
                detail=f"Workspace with ID {workspace_id} not found"
            )
        return transform_workspace_response(workspace)

    async def get_workspace_by_slug(self, slug: str) -> WorkspaceResponse:
        """Get a workspace by Slug."""
        workspace = await self.repository.get_workspace(slug)
        if not workspace:
            return None

        return transform_workspace_response(workspace)

    async def update_workspace(
            self,
            workspace_id: str,
            data: UpdateWorkspaceRequest
    ) -> WorkspaceResponse:
        """Update an existing workspace."""
        workspace = await self.repository.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=404,
                detail=f"Workspace with ID {workspace_id} not found"
            )

        # Update only provided fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(workspace, field, value)

        updated_workspace = await self.repository.update_workspace(workspace)
        return transform_workspace_response(updated_workspace)

    async def delete_workspace(self, workspace_id: str) -> WorkspaceResponse:
        """Delete a workspace."""
        workspace = await self.repository.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=404,
                detail=f"Workspace with ID {workspace_id} not found"
            )

        deleted_workspace = await self.repository.delete_workspace(workspace)
        return transform_workspace_response(deleted_workspace)

    async def get_workspaces_by_account(
            self,
            account_id: str
    ) -> list[WorkspaceResponse]:
        """Get all workspaces for a specific account."""
        workspaces = await self.repository.get_workspaces_by_account(account_id)
        return [transform_workspace_response(w) for w in workspaces]

    async def get_workspaces(
            self,
            page: int = 1,
            size: int = 100,
            account_id: Optional[str] = None
    ) -> WorkspacesListResponse:
        """Get paginated list of workspaces."""
        skip = (page - 1) * size
        workspaces, total = await self.repository.get_workspaces(
            skip=skip,
            limit=size,
            account_id=account_id
        )

        return transform_workspaces_list_response(
            workspaces=workspaces,
            total=total,
            page=page,
            size=size
        )