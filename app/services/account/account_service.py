from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, AccountStatus
from app.repositories.account.account import AccountRepository
from app.core.database import get_session
from app.core.errors import NotFoundError
from app.core.id_generator.id_generator import generate_account_id


class AccountService:
    def __init__(
            self,
            repository: AccountRepository
    ):
        self.repository = repository

    async def create_account(
            self,
            name: str,
            active_plan_id: str = None,
            subscription_status: str = None,
            products_enabled: bool = True
    ) -> Account:
        """Create a new account."""
        try:
            account = Account(
                id=generate_account_id(),
                name=name,
                active_plan_id=active_plan_id,
                subscription_status=subscription_status or AccountStatus.ACTIVE.value,
                products_enabled=products_enabled,
                plan_started_at=datetime.utcnow() if active_plan_id else None
            )

            return await self.repository.create_account(account)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create account: {str(e)}"
            )

    async def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        try:
            account = await self.repository.get_account(account_id)
            if not account:
                raise NotFoundError(
                    message="Account not found",
                    context={"account_id": account_id}
                )
            return account
        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get account: {str(e)}"
            )

    async def update_account(self, account_id: str, update_data: dict) -> Account:
        """Update account information."""
        try:
            account = await self.get_account(account_id)

            allowed_fields = [
                'name',
                'products_enabled',
                'subscription_status'
            ]

            for field in allowed_fields:
                if field in update_data:
                    setattr(account, field, update_data[field])

            return await self.repository.update_account(account)

        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update account: {str(e)}"
            )

    async def update_plan(
            self,
            account_id: str,
            plan_id: str,
            subscription_status: Optional[str] = None
    ) -> Account:
        """Update account's plans and related information."""
        try:
            account = await self.get_account(account_id)
            account.active_plan_id = plan_id
            account.plan_started_at = datetime.utcnow()

            if subscription_status:
                account.subscription_status = subscription_status

            return await self.repository.update_account(account)

        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update account plans: {str(e)}"
            )

    async def update_feature_flags(
            self,
            account_id: str,
            products_enabled: Optional[bool] = None
    ) -> Account:
        """Update account feature flags."""
        try:
            account = await self.get_account(account_id)

            if products_enabled is not None:
                account.products_enabled = products_enabled

            return await self.repository.update_account(account)

        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update feature flags: {str(e)}"
            )

    async def get_accounts_by_subscription_status(self, status: str) -> List[Account]:
        """Get all accounts with a specific subscription status."""
        try:
            return await self.repository.get_accounts_by_subscription_status(status)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get accounts by status: {str(e)}"
            )

    async def get_accounts_by_plan(self, plan_id: str) -> List[Account]:
        """Get all accounts on a specific plans."""
        try:
            return await self.repository.get_accounts_by_plan(plan_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get accounts by plans: {str(e)}"
            )

    # async def update_subscription_status(
    #         self,
    #         account_id: str,
    #         status: str
    # ) -> m:
    #     """Update account's subscription status."""
    #     try:
    #         account = await self.get_account(account_id)
    #         account.subscription_status = status
    #         return await self.repository.update_account(account)
    #     except NotFoundError:
    #         raise
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=500,
    #             detail=f"Failed to update subscription status: {str(e)}"
    #         )