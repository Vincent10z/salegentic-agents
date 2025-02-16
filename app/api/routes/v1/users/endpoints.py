from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create(
        request: Request,
        current_user: Dict = Depends(get_current_user),
        hubspot_service: HubspotService = Depends()
) -> Dict:
    """Initiate HubSpot OAuth flow."""
    auth_url = await hubspot_service.initiate_oauth(current_user["id"])
    return {"authorization_url": auth_url}
