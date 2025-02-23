from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class HubspotCallbackResponse(BaseModel):
    id: str
    workspace_id: str
    provider: str
    hubspot_portal_id: str
    is_active: bool
    account_name: str | None


class HubspotList(BaseModel):
    list_id: str = Field(..., alias="listId", description="The unique identifier of the list")
    name: str = Field(..., description="Name of the list")
    size: int = Field(..., description="Number of contacts in the list")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    processing_status: str = Field(..., alias="processingStatus")
    object_type_id: str = Field(..., alias="objectTypeId")

    class Config:
        allow_population_by_field_name = True


class GetHubspotListsResponse(BaseModel):
    lists: List[HubspotList] = Field(..., description="Array of contact lists")
    total: int = Field(..., description="Total number of lists")
