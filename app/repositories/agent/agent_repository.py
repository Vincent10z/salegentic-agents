# app/repositories/agent/agent_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.models.agent import Conversation, ConversationMessage

class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
            self,
            workspace_id: str,
            user_id: str
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: str) -> Conversation:
        """Get a conversation by ID"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalars().first()

    async def add_message(
            self,
            conversation_id: str,
            role: str,
            content: str
    ) -> ConversationMessage:
        """Add a message to a conversation"""
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message