# app/repositories/agent/agent_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
            workspace_id=workspace_id,
            user_id=user_id
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

    async def get_conversation_messages(self, conversation_id: str):
        """Get all messages for a conversation ordered by creation time"""
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at)
        )
        return result.scalars().all()

    async def add_message(
            self,
            conversation_id: str,
            role: str,
            content: str
    ) -> ConversationMessage:
        """Add a message to a conversation"""
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
