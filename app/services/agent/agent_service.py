# app/services/agent/agent_service.py
from typing import Dict, List, Any, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.v1.agents.response import AgentResponse
from app.models.agent import Conversation, AgentState
from app.services.agent.tools.tool_registry import ToolRegistry
from app.repositories.agent.agent_repository import AgentRepository
from app.services.llm.llm import LLMService


class AgentService:
    def __init__(
            self,
            db: AsyncSession,
            repository: AgentRepository,
            tool_registry: ToolRegistry,
            llm_service: LLMService
    ):
        self.db = db
        self.repository = repository
        self.tool_registry = tool_registry
        self.llm_service = llm_service

    async def process_query(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: Optional[str] = None
    ) -> AgentResponse:
        """Process a user query using ReAct pattern"""

        # Get or create conversation
        conversation = await self._get_or_create_conversation(workspace_id, user_id, conversation_id)

        # Add user message
        message = await self.repository.add_message(conversation.id, "user", query)

        # Get available tools with descriptions
        tools = self.tool_registry.get_tools_with_descriptions()

        # Initialize agent state
        agent_state = {
            "query": query,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "conversation_id": conversation.id,
            "tools": tools,
            "thoughts": [],
            "actions": [],
            "final_answer": None
        }

        # Execute ReAct loop
        max_steps = 5  # Prevent infinite loops
        for step in range(max_steps):
            # Get next action from LLM
            action = await self.llm_service.get_next_action(agent_state)

            # Store the thought process
            agent_state["thoughts"].append(action["thought"])

            # If final answer, break the loop
            if action["action_type"] == "final_answer":
                agent_state["final_answer"] = action["action_input"]
                break

            # Execute tool and get result
            if action["action_type"] == "tool":
                tool_name = action["tool_name"]
                tool_input = action["action_input"]

                # Store the action
                agent_state["actions"].append({
                    "tool": tool_name,
                    "input": tool_input
                })

                # Execute the tool
                tool = self.tool_registry.get_tool_by_name(tool_name)
                if not tool:
                    tool_result = {"error": f"Tool {tool_name} not found"}
                else:
                    tool_result = await tool.execute(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        query=tool_input,
                        conversation_id=conversation.id
                    )

                # Add result to agent state
                agent_state["actions"][-1]["result"] = tool_result

        # Store the final answer
        message = await self.repository.add_message(
            conversation.id,
            "agent",
            agent_state["final_answer"]
        )
        # agent_state["actions"].append(message)

        return AgentResponse(
            conversation_id=str(conversation.id),
            answer=agent_state["final_answer"],
            reasoning=agent_state["thoughts"],
            actions=agent_state["actions"],
        )

    async def _get_or_create_conversation(
            self,
            workspace_id: str,
            user_id: str,
            conversation_id: Optional[str] = None
    )-> Conversation:
        """Get existing conversation or create a new one"""
        if conversation_id:
            conversation = await self.repository.get_conversation(conversation_id)
            if conversation and conversation.workspace_id == workspace_id:
                return conversation

        conversation = await self.repository.create_conversation(
            workspace_id=workspace_id,
            user_id=user_id
        )

        return conversation
