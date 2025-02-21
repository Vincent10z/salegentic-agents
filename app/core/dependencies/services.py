from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.account.account import AccountService
from app.repositories.account.account import AccountRepository
from app.core.database import get_session


def get_account_repository(db: AsyncSession = Depends(get_session)) -> AccountRepository:
    return AccountRepository(db)


def get_account_service(repo: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(repository=repo)
