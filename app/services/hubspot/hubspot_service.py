from typing import Dict, List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..models.oauth_credentials import OAuthCredentials
from ..clients.hubspot.auth import HubspotAuth
from ..clients.hubspot.client import HubspotClient
from ..core.config import settings
from ..core.database import get_session

class HubspotService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db
        self.auth_client = HubspotAuth(
            client_id=settings.HUBSPOT_CLIENT_ID,
            client_secret=settings.HUBSPOT_CLIENT_SECRET,
            redirect_uri=settings.HUBSPOT_REDIRECT_URI
        )

    async def initiate_oauth(self, user_id: str) -> str:
        """Start OAuth flow for HubSpot."""
        state = str(uuid.uuid4())
        # Store state in cache/db for validation
        return self.auth_client.get_authorization_url(state)

    async def handle_oauth_callback(self, code: str, state: str, user_id: str) -> Dict:
        """Handle OAuth callback from HubSpot."""
        # Validate state
        token_data = await self.auth_client.exchange_code(code)

        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

        # Create credentials record
        credentials = OAuthCredentials(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at,
            hubspot_portal_id=token_data["hub_id"],
            account_name=token_data.get("hub_domain")
        )

        self.db.add(credentials)
        await self.db.commit()
        await self.db.refresh(credentials)

        return {
            "status": "success",
            "credentials_id": str(credentials.id)
        }

    async def get_client(self, user_id: str) -> HubspotClient:
        """Get authenticated HubSpot client for user."""
        credentials = await self._get_valid_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=404, detail="No valid HubSpot connection found")

        return HubspotClient(credentials.access_token)

    async def _get_valid_credentials(self, user_id: str) -> Optional[OAuthCredentials]:
        """Get valid credentials, refreshing if necessary."""
        query = select(OAuthCredentials).where(
            OAuthCredentials.user_id == user_id,
            OAuthCredentials.is_active == True
        )

        result = await self.db.execute(query)
        credentials = result.scalar_one_or_none()

        if not credentials:
            return None

        # Check if token needs refresh
        if datetime.utcnow() >= credentials.expires_at:
            token_data = await self.auth_client.refresh_token(credentials.refresh_token)
            credentials.access_token = token_data["access_token"]
            credentials.refresh_token = token_data["refresh_token"]
            credentials.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            await self.db.commit()

        return credentials