from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.analytics.analytics_service import AnalyticsProcessor
from app.services.hubspot.hubspot_service import HubspotService
from app.services.workspace.workspace_service import WorkspaceService
from app.repositories.agent.agent_repository import AgentRepository
from app.repositories.workspace.workspace import WorkspaceRepository


class AgentService:
    def __init__(
            self,
            db: AsyncSession,
            repository: AgentRepository,
            workspace_service: WorkspaceService,
            hubspot_service: HubspotService,
            analytics_processor: AnalyticsProcessor
    ):
        self.db = db
        self.repository = repository
        self.workspace_service = workspace_service
        self.hubspot_service = hubspot_service
        self.analytics_processor = analytics_processor

        self.monitoring_config = {
            "health_check_interval": timedelta(days=1),
            "max_concurrent_analyses": 10
        }


