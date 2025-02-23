from datetime import datetime
from typing import List, Dict, Optional

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


class DealStageMetrics(BaseModel):
    stage_id: str
    name: str
    deals_count: int
    total_value: float
    avg_time_in_stage: float  # in days
    conversion_rate: float  # percentage


class PipelineMetrics(BaseModel):
    pipeline_id: str
    name: str
    total_deals: int
    total_value: float
    avg_deal_size: float
    avg_sales_cycle: float  # in days
    stages: List[DealStageMetrics]


class DealAnalyticsResponse(BaseModel):
    total_deals: int = Field(..., description="Total number of deals in the period")
    total_value: float = Field(..., description="Total value of all deals")
    won_deals: int = Field(..., description="Number of won deals")
    lost_deals: int = Field(..., description="Number of lost deals")
    avg_deal_size: float = Field(..., description="Average deal size")
    avg_sales_cycle: float = Field(..., description="Average sales cycle length in days")
    pipelines: List[PipelineMetrics] = Field(..., description="Pipeline-specific metrics")
    trend_data: Dict = Field(..., description="Time-series data for trends")


class EngagementMetrics(BaseModel):
    type: str
    count: int
    avg_response_time: Optional[float]  # in hours
    success_rate: Optional[float]  # percentage


class EngagementAnalyticsResponse(BaseModel):
    total_engagements: int = Field(..., description="Total number of engagements")
    engagement_types: List[EngagementMetrics] = Field(..., description="Metrics by type")
    daily_trends: Dict = Field(..., description="Daily engagement trends")
    top_performers: List[Dict] = Field(..., description="Top performing team members")


class StageMetrics(BaseModel):
    stage_id: str
    name: str
    deals_count: int
    value: float
    conversion_rate: float
    avg_time: float  # in days


class PipelineAnalyticsResponse(BaseModel):
    pipeline_id: str
    name: str
    total_deals: int = Field(..., description="Total number of deals")
    total_value: float = Field(..., description="Total pipeline value")
    stages: List[StageMetrics] = Field(..., description="Stage-specific metrics")
    velocity: float = Field(..., description="Average deal velocity in days")
    conversion_rates: Dict[str, float] = Field(..., description="Stage-to-stage conversion rates")
    stage_distribution: Dict[str, int] = Field(..., description="Distribution of deals across stages")


class ContactSegmentMetrics(BaseModel):
    segment: str
    count: int
    engagement_rate: float
    conversion_rate: Optional[float]
    avg_deal_value: Optional[float]


class ContactAnalyticsResponse(BaseModel):
    total_contacts: int = Field(..., description="Total number of contacts")
    active_contacts: int = Field(..., description="Number of actively engaged contacts")
    lifecycle_distribution: Dict[str, int] = Field(..., description="Distribution across lifecycle stages")
    engagement_metrics: Dict[str, float] = Field(..., description="Engagement metrics")
    segments: Optional[List[ContactSegmentMetrics]] = Field(None, description="Segment-specific metrics")
    growth_trend: Dict = Field(..., description="Contact growth trends")
