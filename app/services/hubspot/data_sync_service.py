# app/services/crm/crm_sync_service.py
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import uuid

from app.core.id_generator.id_generator import generate_hubspot_deal_snapshot_id
from app.services.hubspot.hubspot_service import HubspotService
from app.repositories.hubspot.deal_repository import DealRepository


class DataSyncService:
    def __init__(
            self,
            db: AsyncSession,
            repository: DealRepository,
            hubspot_service: HubspotService
    ):
        self.db = db
        self.repository = repository
        self.hubspot_service = hubspot_service

    async def sync_hubspot_deals(self, workspace_id: str) -> Dict[str, Any]:
        """Sync deals from HubSpot into our database"""

        hubspot_client = await self.hubspot_service.get_client(workspace_id)
        hubspot_data = await hubspot_client.get_deals_with_pipelines()

        deal_snapshots = []
        for deal in hubspot_data.deals:
            pipeline = next((p for p in hubspot_data.pipelines if p.id == deal.pipeline), None)
            stage = next((s for s in pipeline.stages if s.id == deal.deal_stage), None) if pipeline else None

            days_in_stage = None
            days_in_pipeline = None

            if deal.create_date:
                current_date = datetime.now(timezone.utc)  # Use timezone-aware timestamp
                days_in_pipeline = (current_date - deal.create_date).days

            deal_snapshot = {
                "id": generate_hubspot_deal_snapshot_id(),
                "workspace_id": workspace_id,
                "external_id": deal.id,
                "source": "hubspot",
                "name": getattr(deal, 'name', f"Deal {deal.id}"),
                "amount": deal.amount,
                "pipeline_id": deal.pipeline,
                "stage_id": deal.deal_stage,
                "stage_name": stage.label if stage else None,
                "owner_id": deal.hubspot_owner_id,
                "created_date": deal.create_date,
                "last_modified_date": getattr(deal, 'last_modified_date', None),
                "close_date": deal.close_date,
                "probability": stage.probability if stage else None,
                "days_in_stage": days_in_stage,
                "days_in_pipeline": days_in_pipeline,
                "contact_ids": deal.contact_ids,
                "company_ids": deal.company_ids,
                "properties": {},
                "sync_date": datetime.utcnow()
            }
            deal_snapshots.append(deal_snapshot)

        # Store in database
        await self.repository.upsert_deals(deal_snapshots)

        return {
            "deals_synced": len(deal_snapshots),
            "sync_date": datetime.utcnow().isoformat()
        }
