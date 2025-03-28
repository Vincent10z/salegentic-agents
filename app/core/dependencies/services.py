from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.repositories.agent.agent_repository import AgentRepository
from app.repositories.hubspot.deal_repository import DealRepository
from app.services.account.account_service import AccountService
from app.services.agent.agent_service import AgentService
from app.services.agent.tools.deal_analysis import DealAnalysisTool
from app.services.agent.tools.tool_registry import ToolRegistry
from app.services.agent.tools.vector_retrieval import VectorRetrievalTool
from app.services.hubspot.data_sync_service import DataSyncService
from app.services.llm.llm import LLMService
from app.services.users.users_service import UserService
from app.services.workspace.workspace_service import WorkspaceService
from app.services.hubspot.hubspot_service import HubspotService
from app.services.vector.vector_service import VectorDBService
from app.repositories.vector.vector_store import VectorRepository

from app.repositories.account.account import AccountRepository
from app.repositories.user.user import UserRepository
from app.repositories.workspace.workspace import WorkspaceRepository
from app.repositories.hubspot.hubspot import HubspotRepository


# Repository dependencies
def get_account_repository(
        db: AsyncSession = Depends(get_session)
) -> AccountRepository:
    return AccountRepository(db)


def get_user_repository(
        db: AsyncSession = Depends(get_session)
) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(
        db: AsyncSession = Depends(get_session)
) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_hubspot_repository(
        db: AsyncSession = Depends(get_session)
) -> HubspotRepository:
    return HubspotRepository(db)


def get_vector_repository(
        db: AsyncSession = Depends(get_session)
) -> VectorRepository:
    return VectorRepository(db)


def get_agent_repository(
        db: AsyncSession = Depends(get_session)
) -> AgentRepository:
    return AgentRepository(db)


def get_deal_repository(
        db: AsyncSession = Depends(get_session)
) -> DealRepository:
    return DealRepository(db)


def get_openai_client():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# def get_analytics_processor() -> AnalyticsProcessor:
#     return AnalyticsProcessor()


def get_account_service(
        repo: AccountRepository = Depends(get_account_repository)
) -> AccountService:
    return AccountService(repository=repo)


def get_user_service(
        repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository=repo)


def get_workspace_service(
        repo: WorkspaceRepository = Depends(get_workspace_repository)
) -> WorkspaceService:
    return WorkspaceService(repository=repo)


def get_hubspot_service(
        repo: HubspotRepository = Depends(get_hubspot_repository),
) -> HubspotService:
    return HubspotService(
        repository=repo,
    )


def get_vector_service(
        db: AsyncSession = Depends(get_session),
        repository: VectorRepository = Depends(get_vector_repository),
        openai_client: AsyncOpenAI = Depends(get_openai_client)
) -> VectorDBService:
    return VectorDBService(
        db=db,
        repository=repository,
        openai_client=openai_client
    )


def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY
    )


def get_llm_service(
        openai_client: AsyncOpenAI = Depends(get_openai_client)
) -> LLMService:
    return LLMService(
        openai_client
    )


def get_tool_registry(
        vector_service: VectorDBService = Depends(get_vector_service),
        deal_repository: DealRepository = Depends(get_deal_repository)
) -> ToolRegistry:
    registry = ToolRegistry()

    # Register tools
    registry.register_tool(VectorRetrievalTool(vector_service))
    registry.register_tool(DealAnalysisTool(deal_repository))

    return registry


def get_agent_service(
        db: AsyncSession = Depends(get_session),
        repository: AgentRepository = Depends(get_agent_repository),
        tool_registry: ToolRegistry = Depends(get_tool_registry),
        llm_service: LLMService = Depends(get_llm_service)
) -> AgentService:
    return AgentService(
        db=db,
        repository=repository,
        tool_registry=tool_registry,
        llm_service=llm_service
    )


def get_data_sync_service(
        db: AsyncSession = Depends(get_session),
        repository: DealRepository = Depends(get_deal_repository),
        hubspot_service: HubspotService = Depends(get_hubspot_service)
) -> DataSyncService:
    return DataSyncService(
        db=db,
        repository=repository,
        hubspot_service=hubspot_service
    )

# def get_agent_service(
#         db: AsyncSession = Depends(get_session),
#         repository=Depends(get_agent_repository),
#         workspace_service: WorkspaceService = Depends(get_workspace_service),
#         hubspot_service: HubspotService = Depends(get_hubspot_service),
# ) -> AgentService:
#
#     return AgentService(
#         db=db,
#         # repository=repository,
#         workspace_service=workspace_service,
#         hubspot_service=hubspot_service,
#     )
