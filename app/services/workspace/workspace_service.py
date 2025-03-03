import string
from random import random
from typing import Optional, Tuple, List, Dict
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
    def __init__(
            self,
            repository: WorkspaceRepository
    ):
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

    async def get_workspaces_by_account_id(
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

    async def initialize_workspace_monitoring(
            self,
            workspace_id: str
    ) -> Dict:
        """Initialize monitoring for a new workspace."""
        try:
            workspace = await self.get_workspace(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")

            # TODO: Allow/setup for workspace monitoring settings configuration
        except ValueError:
            return None
        return None

    async def analyze_workspace_health(
            self,
            workspace_id: str,
            force_refresh: bool = False
    ) -> None:
        """
        Analyze workspace health, using cached results if available and recent.
        """
        #TODO: Here we will initialize workspace health sync

    async def get_at_risk_workspaces(self) -> List[Dict]:
        """
        Identify workspaces that are at risk based on recent analyses.
        """
        #TODO: Some monitoring system on cron job that can

    async def update_monitoring_config(
            self,
            workspace_id: str,
            config_updates: Dict
    ) -> Dict:
        """
        Update monitoring configuration for a workspace.
        """

        # TODO: Store in database updated monitoring config
        # Maybe just need to update workspace object tbh

    async def get_health_trend(
            self,
            workspace_id: str,
            days: int = 30
    ) -> List[None]:
        """
        Get health score trend for a workspace over time.
        """

        # TODO: Implement retrieval of historical health scores
        # This would require storing health scores in a database


    async def _get_cached_analysis(
            self,
            workspace_id: str
    ) -> Optional[None]:
        """
        Retrieve cached analysis results if available.
        """
        # TODO: Implement cache retrieval


    async def _cache_analysis_results(
            self,
            workspace_id: str,
            health_score: None
    ):
        """
        Cache analysis results for future use.
        """
        # TODO: Implement caching


    async def _handle_risk_notification(
            self,
            workspace_id: str,
            health_score: None
    ):
        """
        Handle notifications for high-risk accounts.
        """
        # TODO: Implement notification system

