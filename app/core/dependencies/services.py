from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.account.account_service import AccountService
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


def get_account_service(repo: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(repository=repo)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository=repo)


def get_workspace_service(repo: WorkspaceRepository = Depends(get_workspace_repository)) -> WorkspaceService:
    return WorkspaceService(repository=repo)


def get_hubspot_service(repo: HubspotRepository = Depends(get_hubspot_repository)) -> HubspotService:
    return HubspotService(repository=repo)
