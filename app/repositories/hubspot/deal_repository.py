# app/repositories/crm/deal_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from app.models.deal_data import DealSnapshot

class DealRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_deals(self, deal_data_list: List[Dict[str, Any]]) -> List[DealSnapshot]:
        """
        Insert or update multiple deal snapshots

        For each deal, check if it exists (by workspace_id and external_id)
        If it exists, update it; if not, insert a new record
        """
        result_deals = []

        for deal_data in deal_data_list:
            # Check if deal exists
            existing_deal = await self.get_deal_by_external_id(
                deal_data["workspace_id"],
                deal_data["external_id"]
            )

            if existing_deal:
                # Update existing deal
                for key, value in deal_data.items():
                    if key != "id":  # Don't update primary key
                        setattr(existing_deal, key, value)
                result_deals.append(existing_deal)
            else:
                # Create new deal
                new_deal = DealSnapshot(**deal_data)
                self.db.add(new_deal)
                result_deals.append(new_deal)

        # Commit all changes
        await self.db.commit()

        # Refresh all deals to get updated data
        for deal in result_deals:
            await self.db.refresh(deal)

        return result_deals

    async def get_deal_by_external_id(
            self,
            workspace_id: str,
            external_id: str
    ) -> Optional[DealSnapshot]:
        """Get a deal by its external ID and workspace ID"""
        result = await self.db.execute(
            select(DealSnapshot).where(
                DealSnapshot.workspace_id == workspace_id,
                DealSnapshot.external_id == external_id
            )
        )
        return result.scalars().first()

    async def get_deals_by_workspace(
            self,
            workspace_id: str,
            pipeline_id: Optional[str] = None,
            stage_id: Optional[str] = None
    ) -> List[DealSnapshot]:
        """Get all deals for a workspace with optional filters"""
        query = select(DealSnapshot).where(DealSnapshot.workspace_id == workspace_id)

        if pipeline_id:
            query = query.where(DealSnapshot.pipeline_id == pipeline_id)

        if stage_id:
            query = query.where(DealSnapshot.stage_id == stage_id)

        # Always get the latest data
        query = query.order_by(DealSnapshot.sync_date.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_pipeline_stages(self, workspace_id: str) -> Dict[str, List[Dict]]:
        """
        Get all unique pipeline and stage combinations for a workspace
        Returns a dictionary of pipelines with their stages
        """
        # Get all distinct pipeline_id, stage_id, stage_name combinations
        query = select(
            DealSnapshot.pipeline_id,
            DealSnapshot.stage_id,
            DealSnapshot.stage_name
        ).where(
            DealSnapshot.workspace_id == workspace_id
        ).distinct()

        result = await self.db.execute(query)
        rows = result.all()

        # Organize by pipeline
        pipelines = {}
        for pipeline_id, stage_id, stage_name in rows:
            if pipeline_id not in pipelines:
                pipelines[pipeline_id] = []

            pipelines[pipeline_id].append({
                "id": stage_id,
                "name": stage_name
            })

        return pipelines