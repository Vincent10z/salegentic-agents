from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> User:
        """Update existing user."""
        await self.db.commit()
        return user

    async def get_users_by_account(self, account_id: str) -> List[User]:
        """Get all users for a specific account."""
        stmt = select(User).where(User.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_users_by_role(self, account_id: str, role: str) -> List[User]:
        """Get all users with a specific role in an account."""
        stmt = (
            select(User)
            .where(User.account_id == account_id)
            .where(User.account_role == role)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_user_role(self, user_id: str, role: str) -> Optional[User]:
        """Update user's account role."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(account_role=role)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def update_account_association(self, user_id: str, account_id: str) -> Optional[User]:
        """Update user's associated account."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(account_id=account_id)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def get_users_by_source(self, source: str) -> List[User]:
        """Get all users from a specific source."""
        stmt = select(User).where(User.source == source)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_user_profile(
            self,
            user_id: str,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            phone: Optional[str] = None,
            where_found_us: Optional[str] = None
    ) -> Optional[User]:
        """Update user profile information."""
        update_values = {}
        if first_name is not None:
            update_values["first_name"] = first_name
        if last_name is not None:
            update_values["last_name"] = last_name
        if phone is not None:
            update_values["phone"] = phone
        if where_found_us is not None:
            update_values["where_found_us"] = where_found_us

        if update_values:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**update_values)
                .returning(User)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.scalar_one_or_none()
        return await self.get_user(user_id)