from fastapi import Depends, HTTPException, Request
from typing import Dict, Optional

from app.core.dependencies.services import get_hubspot_service
from app.models.hubspot import Hubspot
from app.services.hubspot.hubspot_service import HubspotService


async def initiate_oauth(
        workspace_id: str,
        hubspot_service: HubspotService = Depends(get_hubspot_service)
) -> Dict:
    """Initiate HubSpot OAuth flow."""
    auth_url = await hubspot_service.initiate_oauth(workspace_id)
    return {"authorization_url": auth_url}


async def oauth_callback(
        code: str,
        state: str,
        hubspot_service: HubspotService = Depends(get_hubspot_service)
) -> Hubspot | None:
    """Handle OAuth callback from HubSpot."""
    return await hubspot_service.handle_oauth_callback(code, state)
#
# @router.get("/contacts")
# async def get_contacts(
#         current_user: Dict = Depends(get_current_user),
#         hubspot_service: HubspotService = Depends()
# ) -> List[Dict]:
#     """Get contacts from HubSpot."""
#     client = await hubspot_service.get_client(current_user["id"])
#     return await client.get_contacts()
#
# @router.get("/deals")
# async def get_deals(
#         current_user: Dict = Depends(get_current_user),
#         hubspot_service: HubspotService = Depends()
# ) -> List[Dict]:
#     """Get deals from HubSpot."""
#     client = await hubspot_service.get_client(current_user["id"])
#     return await client.get_deals()
