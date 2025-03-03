# app/api/routes/v1/agent/response.py
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Response model for an agent query"""
    conversation_id: str
    answer: str
    reasoning: List[str] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)


class ConversationMessageResponse(BaseModel):
    """Model for a single conversation message"""
    id: str
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    """Response model for conversation history"""
    conversation_id: str
    workspace_id: str
    user_id: str
    created_at: str
    messages: List[ConversationMessageResponse] = Field(default_factory=list)


class SyncResponse(BaseModel):
    """Response model for data sync operations"""
    deals_synced: int
    sync_date: str


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# Transform functions
def transform_agent_response(
        result: AgentResponse
) -> AgentResponse:
    """Transform agent result to response model"""
    return result


def transform_conversation_response(
        conversation_id: str,
        workspace_id: str,
        user_id: str,
        created_at: datetime,
        messages: List[Any]
) -> ConversationResponse:
    """Transform conversation to response model"""
    return ConversationResponse(
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        user_id=user_id,
        created_at=created_at.isoformat(),
        messages=[
            ConversationMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
    )