import uuid
from http.client import HTTPException
from typing import Optional, List, Dict
from venv import logger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.models.hubspot import Hubspot
from app.repositories.hubspot.hubspot import HubspotRepository
from ...api.routes.v1.integrations.hubspot.response import GetHubspotListsResponse, HubspotList, \
    ContactAnalyticsResponse, PipelineAnalyticsResponse, EngagementAnalyticsResponse, DealAnalyticsResponse
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

    async def get_client(self, workspace_id: str) -> HubspotClient:
        """Get authenticated HubSpot client for user."""
        try:
            credentials = await self._get_valid_credentials(workspace_id)

            if not credentials:
                raise NotFoundError(
                    message="No valid HubSpot record found",
                    context={"workspace_id": workspace_id}
                )

            return HubspotClient(credentials.access_token)

        except Exception as e:
            raise IntegrationError(
                message="Failed to initialize HubSpot client",
                cause=e,
                context={"workspace_id": workspace_id}
            )

    async def _get_valid_credentials(self, workspace_id: str) -> Optional[Hubspot]:
        """Get valid credentials, refreshing if necessary."""
        credentials = await self.repository.get_hubspot_record(workspace_id)

        if not credentials:
            return None

        # Convert current UTC time to be timezone-aware
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        print("Current time:", current_time)
        print("Expires at:", credentials.expires_at)
        print("Expires at type:", type(credentials.expires_at))

        if current_time >= credentials.expires_at:
            token_data = await self.auth_client.refresh_token(credentials.refresh_token)

            credentials.access_token = token_data["access_token"]
            credentials.refresh_token = token_data["refresh_token"]

            credentials.expires_at = (datetime.utcnow().replace(tzinfo=timezone.utc) +
                                      timedelta(seconds=token_data["expires_in"]))
            await self.repository.update_hubspot_record(credentials)

        return credentials

    async def get_account_details(self, access_token: str) -> dict:
        """Get HubSpot account details including portal ID."""
        # Make API call to HubSpot's account info endpoint
        response = await self.session.get(
            "{https://api.hubspot.com/account-info}/v3/details",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return await response.json()

    async def get_hubspot_lists(self, workspace_id: str) -> GetHubspotListsResponse:
        """Get HubSpot lists with contact counts."""
        try:
            client = await self.get_client(workspace_id)
            if not client:
                raise HTTPException(status_code=404, detail="HubSpot integration not found")

            response_data = await client.get_lists()

            lists = [
                HubspotList(
                    list_id=int(list_data["list_id"]),
                    name=str(list_data["name"]),
                    contacts_count=int(list_data["contacts_count"])
                )
                for list_data in response_data.get("lists", [])
            ]

            return GetHubspotListsResponse(
                lists=lists,
                total=response_data.get("total", 0)
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching HubSpot lists: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch HubSpot lists")

    async def get_analytics_data(
            self,
            workspace_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            pipeline_id: Optional[str] = None,
            include_contacts: bool = True,
            include_engagements: bool = True
    ) -> Dict:
        """
        Get comprehensive analytics data from Hubspot.
        This is the main method for fetching data for AI analysis.
        """
        try:
            client = await self.get_client(workspace_id)

            # Set default date range if not provided
            end_date = end_date or datetime.now(timezone.utc)
            start_date = start_date or (end_date - timedelta(days=90))

            # Fetch all necessary data in parallel
            data = await self._fetch_hubspot_data(
                client=client,
                start_date=start_date,
                end_date=end_date,
                pipeline_id=pipeline_id,
                include_contacts=include_contacts,
                include_engagements=include_engagements
            )

            # Process data through analytics processor
            return await self.analytics_processor.prepare_analytics_agent_input(
                workspace_id=workspace_id,
                deals_data=data['deals'],
                pipelines_data=data['pipelines'],
                engagements_data=data.get('engagements'),
                contacts_data=data.get('contacts'),
                start_date=start_date,
                end_date=end_date
            )

        except Exception as e:
            logger.error(f"Error preparing analytics data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to prepare analytics data: {str(e)}"
            )

    async def _fetch_hubspot_data(
            self,
            client: HubspotClient,
            start_date: datetime,
            end_date: datetime,
            pipeline_id: Optional[str] = None,
            include_contacts: bool = True,
            include_engagements: bool = True
    ) -> Dict:
        """Fetch all required data from Hubspot APIs."""
        tasks = {
            'deals': client.get_deals(
                properties=[
                    "amount",
                    "dealstage",
                    "closedate",
                    "pipeline",
                    "createdate",
                    "hubspot_owner_id",
                    "industry"
                ],
                associations=["contacts", "companies"]
            ),
            'pipelines': client.get_pipelines(),
            'analytics': client.get_deal_analytics(
                start_date=start_date,
                end_date=end_date
            )
        }

        if include_contacts:
            tasks['contacts'] = client.get_contacts(
                properties=[
                    "createdate",
                    "lastmodifieddate",
                    "lifecyclestage",
                    "email",
                    "company_size",
                    "industry"
                ],
                limit=1000
            )

        if include_engagements:
            tasks['engagements'] = client.get_engagements(
                engagement_types=["CALL", "EMAIL", "MEETING"],
                limit=1000
            )

        # Execute all API calls concurrently
        results = {}
        for key, task in tasks.items():
            try:
                results[key] = await task
            except Exception as e:
                logger.error(f"Error fetching {key}: {str(e)}")
                results[key] = {'results': []}

        return results

        # Specific analytics methods now delegate to the analytics processor
    async def get_deal_analytics(
            self,
            workspace_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            pipeline_id: Optional[str] = None
    ) -> DealAnalyticsResponse:
        """Get deal analytics using the analytics processor."""
        data = await self.get_analytics_data(
            workspace_id=workspace_id,
            start_date=start_date,
            end_date=end_date,
            pipeline_id=pipeline_id,
            include_contacts=False  # Optimize by only fetching needed data
        )
        return data.deal_metrics

    async def get_engagement_analytics(
            self,
            workspace_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> EngagementAnalyticsResponse:
        """Get engagement analytics using the analytics processor."""
        data = await self.get_analytics_data(
            workspace_id=workspace_id,
            start_date=start_date,
            end_date=end_date,
            include_contacts=False  # Optimize by only fetching needed data
        )
        return data.engagement_metrics

    async def get_pipeline_analytics(
            self,
            workspace_id: str,
            pipeline_id: Optional[str] = None
    ) -> PipelineAnalyticsResponse:
        """Get pipeline analytics using the analytics processor."""
        data = await self.get_analytics_data(
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
            include_contacts=False,
            include_engagements=False
        )
        return data.pipeline_metrics

    async def get_contact_analytics(
            self,
            workspace_id: str,
            segment_property: Optional[str] = None
    ) -> ContactAnalyticsResponse:
        """Get contact analytics using the analytics processor."""
        data = await self.get_analytics_data(
            workspace_id=workspace_id,
            include_engagements=True  # Need engagements for contact analysis
        )
        return data.contact_metrics
