from dataclasses import dataclass
from typing import Dict, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


@dataclass
class AgentState:
    query: str
    workspace_id: str
    user_id: str
    conversation_id: str
    tools: List[Dict[str, str]]
    thoughts: Dict[str, str]
    actions: Dict[str, str]
    final_answer: str
