from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace
from datetime import datetime


class WorkspaceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workspace(self, workspace: Workspace) -> Workspace:
        """Create a new workspace."""
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        stmt = select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        stmt = select(Workspace).where(
            Workspace.slug == slug,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_workspace(self, workspace: Workspace) -> Workspace:
        """Update existing workspace."""
        await self.db.commit()
        return workspace

    async def delete_workspace(self, workspace: Workspace) -> Workspace:
        """Soft delete a workspace by setting deleted_at timestamp."""
        workspace.deleted_at = datetime.now()
        await self.db.commit()
        return workspace

    async def get_workspaces_by_account(self, account_id: str) -> list[Workspace]:
        """Get all workspaces for a specific account."""
        stmt = select(Workspace).where(
            Workspace.account_id == account_id,
            Workspace.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_workspaces(
            self,
            skip: int = 0,
            limit: int = 100,
            account_id: Optional[str] = None
    ) -> tuple[list[Workspace], int]:
        """
        Get paginated list of workspaces with optional account filtering.
        Returns tuple of (workspaces, total_count)
        """
        # Base query for non-deleted workspaces
        query = select(Workspace).where(Workspace.deleted_at.is_(None))

        # Add account filter if provided
        if account_id:
            query = query.where(Workspace.account_id == account_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        workspaces = list(result.scalars().all())

        return workspaces, total