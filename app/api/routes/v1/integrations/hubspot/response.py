from pydantic import BaseModel


class HubspotCallbackResponse(BaseModel):
    id: str
    workspace_id: str
    provider: str
    hubspot_portal_id: str
    is_active: bool
    account_name: str | None