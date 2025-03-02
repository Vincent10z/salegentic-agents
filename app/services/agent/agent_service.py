# app/services/agent/agent_service.py

from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.services.vector.vector_service import VectorDBService
from app.services.agent.tools.tool_registry import ToolRegistry
from app.models.agent import Conversation, ConversationMessage
from app.repositories.agent.agent_repository import AgentRepository

class AgentService:
    def __init__(
            self,
            db: AsyncSession,
            repository: AgentRepository,
            tool_registry: ToolRegistry,
            vector_service: VectorDBService
    ):
        self.db = db
        self.repository = repository
        self.tool_registry = tool_registry
        self.vector_service = vector_service

    async def process_query(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user query and return a response using available tools"""

        # Get or create conversation context
        conversation = await self._get_or_create_conversation(workspace_id, user_id, conversation_id)

        # Add user message to conversation history
        await self._add_message_to_conversation(conversation.id, "user", query)

        # Find appropriate tool for the query
        tool = self.tool_registry.get_tool_for_query(query)

        # Execute the tool
        result = await tool.execute(workspace_id, user_id, query, conversation.id)

        # Add agent response to conversation history
        await self._add_message_to_conversation(conversation.id, "agent", result["answer"])

        # Return the response
        return {
            "conversation_id": conversation.id,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    async def _get_or_create_conversation(
            self,
            workspace_id: str,
            user_id: str,
            conversation_id: Optional[str] = None
    ) -> Conversation:
        if conversation_id:
            conversation = await self.repository.get_conversation(conversation_id)
            if conversation and conversation.workspace_id == workspace_id:
                return conversation

        # Create new conversation
        return await self.repository.create_conversation(
            workspace_id=workspace_id,
            user_id=user_id
        )

    async def _add_message_to_conversation(
            self,
            conversation_id: str,
            role: str,  # "user" or "agent"
            content: str
    ) -> None:
        await self.repository.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )