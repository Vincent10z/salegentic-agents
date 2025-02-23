from asyncio.log import logger
from http.client import HTTPException
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime

from app.api.routes.v1.integrations.hubspot.response import GetHubspotListsResponse


class HubspotClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com"

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to HubSpot API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method,
                    f"{self.base_url}/{endpoint}",
                    headers=headers,
                    json=data
            ) as response:
                if response.status not in [200, 201]:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"HubSpot API error: {await response.text()}"
                    )
                return await response.json()

    async def get_contacts(self, limit: int = 100) -> List[Dict]:
        """Get contacts from HubSpot."""
        endpoint = f"crm/v3/objects/contacts?limit={limit}"
        return await self._make_request("GET", endpoint)

    async def get_deals(self, limit: int = 100) -> List[Dict]:
        """Get deals from HubSpot."""
        endpoint = f"crm/v3/objects/deals?limit={limit}"
        return await self._make_request("GET", endpoint)

    async def get_lists(self, limit: int = 100) -> dict:
        """Get HubSpot lists."""
        try:
            endpoint = f"crm/v3/lists?limit={limit}&includeFilters=false"
            response = await self._make_request("GET", endpoint)

            lists_data = []
            for list_item in response.get("lists", []):
                lists_data.append({
                    "listId": list_item["listId"],
                    "name": list_item["name"],
                    "size": list_item["size"]
                })

            return {
                "lists": lists_data,
                "total": len(lists_data)
            }

        except Exception as e:
            logger.error(f"Error in HubSpot API call: {str(e)}")
            raise HTTPException(500, "Failed to fetch HubSpot lists")

    async def get_deals(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None,
            associations: Optional[List[str]] = None
    ) -> Dict:
        """
        Get deals with optional properties and associations.

        Args:
            limit: Number of deals to return
            properties: List of deal properties to include
            after: Continuation token for pagination
            associations: List of objects to associate (contacts, companies, etc.)
            """
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after
        if associations:
            params["associations"] = associations

        return await self._make_request(
            "GET",
            "crm/v3/objects/deals",
            params=params
        )

    async def get_deal(self, deal_id: str, properties: Optional[List[str]] = None) -> Dict:
        """Get detailed information about a specific deal."""
        params = {}
        if properties:
            params["properties"] = properties

        return await self._make_request(
            "GET",
            f"crm/v3/objects/deals/{deal_id}",
            params=params
        )

    # Pipeline Methods
    async def get_pipelines(self) -> Dict:
        """Get all deal pipelines and their stages."""
        return await self._make_request("GET", "crm/v3/pipelines/deals")

    async def get_pipeline_stages(self, pipeline_id: str) -> Dict:
        """Get stages for a specific pipeline."""
        return await self._make_request(
            "GET",
            f"crm/v3/pipelines/deals/{pipeline_id}/stages"
        )

    # Contact Methods
    async def get_contacts(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None
    ) -> Dict:
        """Get contacts with optional properties."""
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after

        return await self._make_request(
            "GET",
            "crm/v3/objects/contacts",
            params=params
        )

    async def get_contact(
            self,
            contact_id: str,
            properties: Optional[List[str]] = None
    ) -> Dict:
        """Get detailed information about a specific contact."""
        params = {}
        if properties:
            params["properties"] = properties

        return await self._make_request(
            "GET",
            f"crm/v3/objects/contacts/{contact_id}",
            params=params
        )

    # Company Methods
    async def get_companies(
            self,
            limit: int = 100,
            properties: Optional[List[str]] = None,
            after: Optional[str] = None
    ) -> Dict:
        """Get companies with optional properties."""
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        if after:
            params["after"] = after

        return await self._make_request(
            "GET",
            "crm/v3/objects/companies",
            params=params
        )

    # Engagement Methods
    async def get_engagements(
            self,
            limit: int = 100,
            after: Optional[str] = None,
            engagement_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Get engagement data (calls, emails, meetings, etc.).

        Args:
            limit: Number of engagements to return
            after: Continuation token for pagination
            engagement_types: List of types to include (CALL, EMAIL, MEETING, etc.)
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        if engagement_types:
            params["types"] = engagement_types

        return await self._make_request(
            "GET",
            "crm/v3/objects/engagements",
            params=params
        )

    async def get_engagement_activity(self, engagement_id: str) -> Dict:
        """Get detailed information about a specific engagement."""
        return await self._make_request(
            "GET",
            f"crm/v3/objects/engagements/{engagement_id}"
        )

    # Property Methods
    async def get_properties(self, object_type: str) -> Dict:
        """
        Get all properties for a specific object type.

        Args:
            object_type: The object type (contacts, companies, deals, etc.)
        """
        return await self._make_request(
            "GET",
            f"crm/v3/properties/{object_type}"
        )

    # Analytics Methods
    async def get_deal_analytics(
            self,
            start_date: datetime,
            end_date: datetime,
            interval: str = "MONTHLY"
    ) -> Dict:
        """
        Get analytics data for deals.

        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            interval: Time interval (DAILY, WEEKLY, MONTHLY)
        """
        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "interval": interval
        }
        return await self._make_request(
            "GET",
            "analytics/v2/reports/deals",
            params=params
        )

    # Association Methods
    async def get_associations(
            self,
            object_type: str,
            object_id: str,
            to_object_type: str
    ) -> Dict:
        """
        Get associations between objects.

        Args:
            object_type: Source object type (deals, contacts, etc.)
            object_id: Source object ID
            to_object_type: Target object type to find associations with
        """
        return await self._make_request(
            "GET",
            f"crm/v3/objects/{object_type}/{object_id}/associations/{to_object_type}"
        )

    # Batch Methods
    async def batch_get_deals(self, deal_ids: List[str]) -> Dict:
        """Get multiple deals in a single request."""
        data = {"inputs": [{"id": id} for id in deal_ids]}
        return await self._make_request(
            "POST",
            "crm/v3/objects/deals/batch/read",
            data=data
        )

    async def batch_get_contacts(self, contact_ids: List[str]) -> Dict:
        """Get multiple contacts in a single request."""
        data = {"inputs": [{"id": id} for id in contact_ids]}
        return await self._make_request(
            "POST",
            "crm/v3/objects/contacts/batch/read",
            data=data
        )
