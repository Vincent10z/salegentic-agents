from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DealStage(str, Enum):
    APPOINTMENT_SCHEDULED = "appointmentscheduled"
    QUALIFIED_TO_BUY = "qualifiedtobuy"
    PRESENTATION_SCHEDULED = "presentationscheduled"
    DECISION_MAKER_BOUGHT_IN = "decisionmakerboughtin"
    CONTRACT_SENT = "contractsent"
    CLOSED_WON = "closedwon"
    CLOSED_LOST = "closedlost"


class EngagementType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    TASK = "TASK"


class DealMetricsModel(BaseModel):
    """Core deal metrics for analysis"""
    total_value: float = Field(..., description="Total value of all deals in the pipeline")
    average_deal_size: float = Field(..., description="Average deal size")
    win_rate: float = Field(..., description="Ratio of won deals to total deals")
    average_sales_cycle_days: float = Field(..., description="Average days from creation to close")
    total_deals: int = Field(..., description="Total number of deals")
    active_deals: int = Field(..., description="Number of active deals")


class PipelineMetricsModel(BaseModel):
    """Pipeline stage metrics"""
    stages: Dict[DealStage, int] = Field(..., description="Number of deals in each stage")
    conversion_rates: Dict[DealStage, float] = Field(..., description="Conversion rate between stages")
    avg_time_in_stage: Dict[DealStage, float] = Field(..., description="Average days spent in each stage")
    stage_value: Dict[DealStage, float] = Field(..., description="Total value of deals in each stage")


class DealTrendsModel(BaseModel):
    """Monthly deal trends"""
    monthly_counts: Dict[str, int] = Field(..., description="Number of deals by month")
    monthly_values: Dict[str, float] = Field(..., description="Deal values by month")
    growth_rate: float = Field(..., description="Month-over-month growth rate")
    seasonal_patterns: Dict[str, float] = Field(..., description="Identified seasonal patterns")


class EngagementMetricsModel(BaseModel):
    """Engagement activity metrics"""
    total_activities: int = Field(..., description="Total number of engagement activities")
    activity_by_type: Dict[EngagementType, int] = Field(..., description="Activities broken down by type")
    response_rates: Dict[EngagementType, float] = Field(..., description="Response rates by engagement type")
    avg_response_time: Dict[EngagementType, float] = Field(..., description="Average response time in hours")
    engagement_effectiveness: float = Field(..., description="Overall engagement effectiveness score")


class ContactMetricsModel(BaseModel):
    """Contact-related metrics"""
    total_contacts: int = Field(..., description="Total number of contacts")
    active_contacts: int = Field(..., description="Number of active contacts")
    engagement_rate: float = Field(..., description="Percentage of contacts engaged")
    lead_conversion_rate: float = Field(..., description="Lead to customer conversion rate")
    avg_interactions_per_contact: float = Field(..., description="Average interactions per contact")


class RiskMetricsModel(BaseModel):
    """Risk analysis metrics"""
    at_risk_deals: List[str] = Field(..., description="IDs of deals identified as at risk")
    risk_factors: Dict[str, float] = Field(..., description="Identified risk factors and their weights")
    risk_score: float = Field(..., description="Overall risk score")
    recommended_actions: List[str] = Field(..., description="Recommended actions to mitigate risks")


class OpportunityMetricsModel(BaseModel):
    """Opportunity analysis metrics"""
    high_value_prospects: List[str] = Field(..., description="IDs of high-value prospects")
    upsell_opportunities: List[str] = Field(..., description="IDs of accounts with upsell potential")
    growth_segments: Dict[str, float] = Field(..., description="Identified growth segments")
    recommended_focus_areas: List[str] = Field(..., description="Recommended areas to focus on")


class AnalyticsAgentInput(BaseModel):
    """Main model for data passed to the analytics agent"""
    workspace_id: str = Field(..., description="ID of the workspace being analyzed")
    time_period: str = Field(..., description="Time period of the analysis")
    deal_metrics: DealMetricsModel
    pipeline_metrics: PipelineMetricsModel
    deal_trends: DealTrendsModel
    engagement_metrics: Optional[EngagementMetricsModel]
    contact_metrics: Optional[ContactMetricsModel]
    risk_metrics: Optional[RiskMetricsModel]
    opportunity_metrics: Optional[OpportunityMetricsModel]

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "ws_123456",
                "time_period": "2024-01-01/2024-03-31",
                "deal_metrics": {
                    "total_value": 1000000.0,
                    "average_deal_size": 50000.0,
                    "win_rate": 0.35,
                    "average_sales_cycle_days": 45.0,
                    "total_deals": 20,
                    "active_deals": 15
                },
                # ... other metrics examples ...
            }
        }


class InsightType(str, Enum):
    """Types of insights that can be generated"""
    PERFORMANCE = "performance"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    TREND = "trend"
    RECOMMENDATION = "recommendation"


class Insight(BaseModel):
    """Structure for individual insights"""
    type: InsightType
    title: str = Field(..., description="Short title describing the insight")
    description: str = Field(..., description="Detailed description of the insight")
    metrics: Dict[str, float] = Field(..., description="Relevant metrics supporting the insight")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence level in the insight")
    priority: int = Field(..., ge=1, le=5, description="Priority level of the insight")
    recommended_actions: Optional[List[str]] = Field(None, description="Suggested actions based on the insight")


class AnalyticsAgentOutput(BaseModel):
    """Structure for analytics agent output"""
    workspace_id: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    time_period: str
    insights: List[Insight]
    summary: str = Field(..., description="Executive summary of the analysis")
    key_metrics: Dict[str, float] = Field(..., description="Key metrics highlighted by the analysis")
    recommendations: List[str] = Field(..., description="Overall recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "ws_123456",
                "analysis_date": "2024-03-23T10:30:00Z",
                "time_period": "2024-Q1",
                "insights": [
                    {
                        "type": "performance",
                        "title": "Improving Win Rate",
                        "description": "Win rate has increased by 15% this quarter",
                        "metrics": {"win_rate_change": 0.15},
                        "confidence_score": 0.95,
                        "priority": 1,
                        "recommended_actions": ["Continue current sales training program"]
                    }
                ]
            }
        }