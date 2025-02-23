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
