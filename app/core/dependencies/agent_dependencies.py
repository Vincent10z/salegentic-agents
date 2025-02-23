from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.agent.agent_repository import AgentRepository
from app.services.agent.agent_service import AgentService
from app.services.analytics.analytics_service import AnalyticsProcessor
from app.services.agent.hubspot.account_health_agent.account_health import AccountHealthAgent
from app.services.agent.hubspot.account_health_agent.recommendations_engine import LLMRecommendationEngine
from app.services.workspace.workspace_service import WorkspaceService
from app.core.dependencies.services import (
    get_analytics_processor,
    get_workspace_service,
    get_recommendation_engine
)


def get_agent_repository(db: AsyncSession = Depends(get_session)) -> AgentRepository:
    return AgentRepository(db)


def get_account_health_agent(
        analytics_processor: AnalyticsProcessor = Depends(get_analytics_processor),
        recommendation_engine: LLMRecommendationEngine = Depends(get_recommendation_engine)
) -> AccountHealthAgent:
    return AccountHealthAgent(
        analytics_processor=analytics_processor,
        llm_client=recommendation_engine.llm_client
    )


def get_agent_service(
        db: AsyncSession = Depends(get_session),
        repository: AgentRepository = Depends(get_agent_repository),
        workspace_service: WorkspaceService = Depends(get_workspace_service),
        account_health_agent: AccountHealthAgent = Depends(get_account_health_agent),
        recommendation_engine: LLMRecommendationEngine = Depends(get_recommendation_engine),
        analytics_processor: AnalyticsProcessor = Depends(get_analytics_processor)
) -> AgentService:
    """Get an instance of the AgentService with all required dependencies."""
    return AgentService(
        db=db,
        repository=repository,
        workspace_service=workspace_service,
        account_health_agent=account_health_agent,
        recommendation_engine=recommendation_engine,
        analytics_processor=analytics_processor
    )
