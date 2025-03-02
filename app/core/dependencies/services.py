from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.account.account_service import AccountService
from app.services.agent.agent_service import AgentService
from app.services.users.users_service import UserService
from app.services.workspace.workspace_service import WorkspaceService
from app.services.hubspot.hubspot_service import HubspotService
from app.services.analytics.analytics_service import AnalyticsProcessor
from app.services.vector.vector_service import VectorDBService
from app.repositories.vector.vector_store import VectorDBRepository

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


def get_vector_db_repository(db: AsyncSession = Depends(get_session)) -> VectorDBRepository:
    return VectorDBRepository(db)


def get_openai_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_analytics_processor() -> AnalyticsProcessor:
    return AnalyticsProcessor()


def get_llm_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


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


def get_vector_db_service(
        db: AsyncSession = Depends(get_session),
        repository: VectorDBRepository = Depends(get_vector_db_repository),
        openai_client: AsyncOpenAI = Depends(get_openai_client)
) -> VectorDBService:
    return VectorDBService(db=db, repository=repository, openai_client=openai_client)


def get_agent_service(
        db: AsyncSession = Depends(get_session),
        # repository=Depends(get_agent_repository),
        workspace_service: WorkspaceService = Depends(get_workspace_service),
        hubspot_service: HubspotService = Depends(get_hubspot_service),
        analytics_processor: AnalyticsProcessor = Depends(get_analytics_processor),
) -> AgentService:

    return AgentService(
        db=db,
        # repository=repository,
        workspace_service=workspace_service,
        hubspot_service=hubspot_service,
        analytics_processor=analytics_processor
    )
