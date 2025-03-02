from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, List
from collections import defaultdict

from app.models.hubspot import (
    HubspotDeal,
    HubspotPipelineStage,
    HubspotEngagement,
    HubspotContact,
    HubspotPipeline,
    HubspotData
)

from app.models.analytics_agent import (
    AnalyticsAgentInput,
    DealMetricsModel,
    PipelineMetricsModel,
    DealTrendsModel,
    EngagementMetricsModel,
    ContactMetricsModel,
    RiskMetricsModel,
    OpportunityMetricsModel,
    DealStage,
    EngagementType
)


class AnalyticsProcessor:
    @staticmethod
    async def prepare_analytics_agent_input(
            workspace_id: str,
            hubspot_data: HubspotData,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> AnalyticsAgentInput:
        """
        Process Hubspot data into structured input for the analytics agent.

        Args:
            workspace_id: The workspace identifier
            hubspot_data: Container with all Hubspot data
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            AnalyticsAgentInput: Structured data for the analytics agent
        """
        #