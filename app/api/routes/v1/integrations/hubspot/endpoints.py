from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List


router = APIRouter()

# @router.get("/connect")
# async def initiate_oauth(
#         request: Request,
#         current_user: Dict = Depends(get_current_user),
#         hubspot_service: HubspotService = Depends()
# ) -> Dict:
#     """Initiate HubSpot OAuth flow."""
#     auth_url = await hubspot_service.initiate_oauth(current_user["id"])
#     return {"authorization_url": auth_url}

# @router.get("/callback")
# async def oauth_callback(
#         code: str,
#         state: str,
#         current_user: Dict = Depends(get_current_user),
#         hubspot_service: HubspotService = Depends()
# ) -> Dict:
#     """Handle OAuth callback from HubSpot."""
#     return await hubspot_service.handle_oauth_callback(code, state, current_user["id"])
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