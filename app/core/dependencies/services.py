from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.agent.agent_service import AgentService, get_agent_repository, get_account_health_agent
from app.services.account.account_service import AccountService
from app.services.users.users_service import UserService
from app.services.workspace.workspace_service import WorkspaceService
from app.services.hubspot.hubspot_service import HubspotService
from app.services.analytics.analytics_service import AnalyticsProcessor
from app.services.agent.hubspot.account_health_agent.recommendations_engine import LLMRecommendationEngine

from app.repositories.account.account import AccountRepository
from app.repositories.user.user import UserRepository
from app.repositories.workspace.workspace import WorkspaceRepository
from app.repositories.hubspot.hubspot import HubspotRepository


# Repository dependencies
def get_account_repository(db: AsyncSession = Depends(get_session)) -> AccountRepository:
    return AccountRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(db: AsyncSession = Depends(get_session)) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_hubspot_repository(db: AsyncSession = Depends(get_session)) -> HubspotRepository:
    return HubspotRepository(db)


# Analytics processor dependency
def get_analytics_processor() -> AnalyticsProcessor:
    return AnalyticsProcessor()


def get_llm_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_recommendation_engine(
        llm_client=Depends(get_llm_client)
) -> LLMRecommendationEngine:
    return LLMRecommendationEngine(llm_client=llm_client)


# Service dependencies
def get_account_service(repo: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(repository=repo)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository=repo)


def get_workspace_service(repo: WorkspaceRepository = Depends(get_workspace_repository)) -> WorkspaceService:
    return WorkspaceService(repository=repo)


def get_hubspot_service(
        repo: HubspotRepository = Depends(get_hubspot_repository),
        analytics_processor: AnalyticsProcessor = Depends(get_analytics_processor)
) -> HubspotService:
    return HubspotService(
        repository=repo,
        analytics_processor=analytics_processor
    )


def get_agent_service(
        db: AsyncSession = Depends(get_session),
        repository = Depends(get_agent_repository),
        workspace_service: WorkspaceService = Depends(get_workspace_service),
        hubspot_service: HubspotService = Depends(get_hubspot_service),
        analytics_processor: AnalyticsProcessor = Depends(get_analytics_processor),
        recommendation_engine: LLMRecommendationEngine = Depends(get_recommendation_engine)
) -> AgentService:
    account_health_agent = get_account_health_agent(
        hubspot_service=hubspot_service,
        analytics_processor=analytics_processor,
        recommendation_engine=recommendation_engine
    )

    return AgentService(
        db=db,
        repository=repository,
        workspace_service=workspace_service,
        hubspot_service=hubspot_service,
        account_health_agent=account_health_agent,
        recommendation_engine=recommendation_engine,
        analytics_processor=analytics_processor
    )