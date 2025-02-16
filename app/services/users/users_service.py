from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user.user import UserRepository
from app.core.database import get_session
from app.core.errors import NotFoundError


class UserService:
    def __init__(
            self,
            db: AsyncSession = Depends(get_session),
            repository: UserRepository = None
    ):
        self.repository = repository or UserRepository(db)

    async def create_user(
            self,
            email: str,
            first_name: str = None,
            last_name: str = None,
            account_id: str = None,
            phone: str = None,
            where_found_us: str = None,
            account_role: str = 'standard',
            source: str = 'sf'
    ) -> User:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = await self.repository.get_user_by_email(email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                account_id=account_id,
                phone=phone,
                where_found_us=where_found_us,
                account_role=account_role,
                source=source
            )

            return await self.repository.create_user(user)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create user: {str(e)}"
            )

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user = await self.repository.get_user(user_id)
            if not user:
                raise NotFoundError(
                    message="User not found",
                    context={"user_id": user_id}
                )
            return user
        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            user = await self.repository.get_user_by_email(email)
            if not user:
                raise NotFoundError(
                    message="User not found",
                    context={"email": email}
                )
            return user
        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user: {str(e)}"
            )

    async def update_user(self, user_id: str, update_data: dict) -> User:
        """Update user information."""
        try:
            user = await self.get_user(user_id)

            # Update allowed fields
            allowed_fields = [
                'first_name',
                'last_name',
                'email',
                'phone',
                'where_found_us',
                'account_role',
                'account_id'
            ]

            for field in allowed_fields:
                if field in update_data:
                    setattr(user, field, update_data[field])

            return await self.repository.update_user(user)

        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update user: {str(e)}"
            )

    async def get_account_users(self, account_id: str) -> List[User]:
        """Get all users for an account."""
        try:
            return await self.repository.get_users_by_account(account_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get account users: {str(e)}"
            )

    async def update_user_role(self, user_id: str, role: str) -> User:
        """Update user's role in the account."""
        try:
            user = await self.get_user(user_id)
            user.account_role = role
            return await self.repository.update_user(user)
        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update user role: {str(e)}"
            )

    async def update_user_account(self, user_id: str, account_id: str) -> User:
        """Update user's associated account."""
        try:
            user = await self.get_user(user_id)
            user.account_id = account_id
            return await self.repository.update_user(user)
        except NotFoundError:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update user account: {str(e)}"
            )