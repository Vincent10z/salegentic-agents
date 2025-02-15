from typing import Dict, List, Optional
import aiohttp
from datetime import datetime

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