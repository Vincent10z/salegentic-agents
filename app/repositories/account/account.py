from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.account import Account


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, account: Account) -> Account:
        """Create a new account."""
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        stmt = select(Account).where(Account.id == account_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_account(self, account: Account) -> Account:
        """Update existing account."""
        await self.db.commit()
        return account

    async def get_accounts_by_subscription_status(self, status: str) -> List[Account]:
        """Get all accounts with a specific subscription status."""
        stmt = select(Account).where(Account.subscription_status == status)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_subscription_status(self, account_id: str, status: str) -> Optional[Account]:
        """Update account subscription status."""
        stmt = (
            update(Account)
            .where(Account.id == account_id)
            .values(subscription_status=status)
            .returning(Account)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def update_feature_flags(
            self,
            account_id: str,
            warmup_enabled: Optional[bool] = None,
            products_enabled: Optional[bool] = None
    ) -> Optional[Account]:
        """Update account feature flags."""
        update_values = {}
        if warmup_enabled is not None:
            update_values["warmup_enabled"] = warmup_enabled
        if products_enabled is not None:
            update_values["products_enabled"] = products_enabled

        if update_values:
            stmt = (
                update(Account)
                .where(Account.id == account_id)
                .values(**update_values)
                .returning(Account)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.scalar_one_or_none()
        return await self.get_account(account_id)

    async def update_plan(
            self,
            account_id: str,
            plan_id: str,
            plan_started_at: datetime = None
    ) -> Optional[Account]:
        """Update account's active plan and plan start date."""
        update_values = {
            "active_plan_id": plan_id,
            "plan_started_at": plan_started_at or datetime.utcnow()
        }
        stmt = (
            update(Account)
            .where(Account.id == account_id)
            .values(**update_values)
            .returning(Account)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def get_accounts_by_plan(self, plan_id: str) -> List[Account]:
        """Get all accounts with a specific plan."""
        stmt = select(Account).where(Account.active_plan_id == plan_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()