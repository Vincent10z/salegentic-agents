from pydantic import BaseModel, Field
from typing import Optional


class AgentQueryRequest(BaseModel):
    """Request model for querying the agent"""
    query: str
    user_id: str
    conversation_id: Optional[str] = None