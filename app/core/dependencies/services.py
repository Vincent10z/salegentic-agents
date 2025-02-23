from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.agent.agent_repository import AgentRepository
from app.services.account.account_service import AccountService
from app.services.agent.agent_service import AgentService
from app.services.agent.hubspot.account_health_agent.account_health import AccountHealthAgent
from app.services.agent.hubspot.account_health_agent.recommendations_engine import LLMRecommendationEngine
from app.services.users.users_service import UserService
from app.services.workspace.workspace_service import WorkspaceService
from app.services.hubspot.hubspot_service import HubspotService

from app.repositories.account.account import AccountRepository
from app.repositories.user.user import UserRepository
from app.repositories.workspace.workspace import WorkspaceRepository
from app.repositories.hubspot.hubspot import HubspotRepository

from app.core.database import get_session


def get_account_repository(db: AsyncSession = Depends(get_session)) -> AccountRepository:
    return AccountRepository(db)


def get_user_repository(db: UserRepository = Depends(get_session)) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(db: AsyncSession = Depends(get_session)) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_hubspot_repository(db: AsyncSession = Depends(get_session)) -> HubspotRepository:
    return HubspotRepository(db)


def get_agent_repository(db: AsyncSession = Depends(get_session)) -> AgentRepository:
    return AgentRepository(db)


def get_account_service(repo: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(repository=repo)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository=repo)


def get_workspace_service(repo: WorkspaceRepository = Depends(get_workspace_repository)) -> WorkspaceService:
    return WorkspaceService(repository=repo)


def get_hubspot_service(repo: HubspotRepository = Depends(get_hubspot_repository)) -> HubspotService:
    return HubspotService(repository=repo)


def get_llm_client():
    # Initialize your chosen LLM client (OpenAI, Anthropic, etc.)
    # This could be moved to a separate LLM service if needed
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_recommendation_engine(
        llm_client=Depends(get_llm_client)
) -> LLMRecommendationEngine:
    return LLMRecommendationEngine(llm_client=llm_client)


def get_account_health_agent(
        hubspot_service: HubspotService = Depends(get_hubspot_service),
        recommendation_engine: LLMRecommendationEngine = Depends(get_recommendation_engine)
) -> AccountHealthAgent:
    return AccountHealthAgent(
        hubspot_service=hubspot_service,
        analytics_processor=hubspot_service.analytics_processor,
        llm_client=recommendation_engine.llm_client
    )


def get_agent_service(
        db: AsyncSession = Depends(get_session),
        agent_repository: AgentRepository = Depends(get_agent_repository),
        workspace_service: WorkspaceService = Depends(get_workspace_service),
        account_health_agent: AccountHealthAgent = Depends(get_account_health_agent),
        recommendation_engine: LLMRecommendationEngine = Depends(get_recommendation_engine)
) -> AgentService:
    return AgentService(
        db=db,
        repository=agent_repository,
        workspace_service=workspace_service,
        account_health_agent=account_health_agent,
        recommendation_engine=recommendation_engine
    )
