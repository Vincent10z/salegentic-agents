from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.integrations.hubspot.hubspot import Hubspot


class HubspotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_hubspot_record(self, credentials: Hubspot) -> Hubspot:
        """Create new HubSpot credentials."""
        self.db.add(credentials)
        await self.db.commit()
        await self.db.refresh(credentials)
        return credentials

    async def get_hubspot_record(self, user_id: str) -> Optional[Hubspot]:
        """Get active credentials for a user."""
        stmt = (
            select(Hubspot)
            .where(Hubspot.user_id == user_id)
            .where(Hubspot.is_active)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_hubspot_record(self, credentials: Hubspot) -> Hubspot:
        """Update existing credentials."""
        await self.db.commit()
        return credentials
