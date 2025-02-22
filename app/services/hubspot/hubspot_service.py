import uuid
from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.hubspot import Hubspot
from app.repositories.hubspot.hubspot import HubspotRepository
from ...clients.hubspot.auth import HubspotAuth
from ...clients.hubspot.client import HubspotClient
from ...core.config import settings
from ...core.database import get_session
from app.core.errors import NotFoundError, IntegrationError
from app.core.id_generator.id_generator import generate_hubspot_id


class HubspotService:
    def __init__(
            self,
            db: AsyncSession = Depends(get_session),
            repository: HubspotRepository = None
    ):
        self.repository = repository or HubspotRepository(db)
        self.auth_client = HubspotAuth(
            client_id=settings.HUBSPOT_CLIENT_ID,
            app_id=settings.HUBSPOT_APP_ID,
            client_secret=settings.HUBSPOT_CLIENT_SECRET,
            redirect_uri=settings.HUBSPOT_REDIRECT_URI
        )

    async def initiate_oauth(self, workspace_id: str) -> str:
        """Start OAuth flow for HubSpot."""
        random_state = str(uuid.uuid4())
        state = f"{workspace_id}:{random_state}"

        return self.auth_client.get_authorization_url(state)

    async def handle_oauth_callback(self, code: str, state: str) -> Optional[Hubspot]:
        """Handle OAuth callback from HubSpot."""
        workspace_id = state.split(":")[0]

        token_data = await self.auth_client.exchange_code(code)
        expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

        # Get account details first using the access token
        account_details = await self.auth_client.get_account_details(token_data["access_token"])

        # Create record with all required data
        record = Hubspot(
            workspace_id=workspace_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at,
            hubspot_portal_id=str(account_details["portalId"]),
            account_name=token_data.get("hub_domain")
        )

        saved_credentials = await self.repository.create_hubspot_record(record)
        return saved_credentials

    async def get_client(self, user_id: str) -> HubspotClient:
        """Get authenticated HubSpot client for user."""
        try:
            credentials = await self._get_valid_credentials(user_id)

            if not credentials:
                raise NotFoundError(
                    message="No valid HubSpot record found",
                    context={"user_id": user_id}
                )

            return HubspotClient(credentials.access_token)

        except Exception as e:
            raise IntegrationError(
                message="Failed to initialize HubSpot client",
                cause=e,
                context={"user_id": user_id}
            )

    async def _get_valid_credentials(self, user_id: str) -> Optional[Hubspot]:
        """Get valid credentials, refreshing if necessary."""
        credentials = await self.repository.get_hubspot_record(user_id)

        if not credentials:
            return None

        # Check if token needs refresh
        if datetime.utcnow() >= credentials.expires_at:
            token_data = await self.auth_client.refresh_token(credentials.refresh_token)

            credentials.access_token = token_data["access_token"]
            credentials.refresh_token = token_data["refresh_token"]

            credentials.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            await self.repository.update_hubspot_record(credentials)

        return credentials

    async def get_account_details(self, access_token: str) -> dict:
        """Get HubSpot account details including portal ID."""
        # Make API call to HubSpot's account info endpoint
        # This is just an example - adjust the endpoint and headers as needed
        response = await self.session.get(
            "{https://api.hubspot.com/account-info}/v3/details",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return await response.json()
