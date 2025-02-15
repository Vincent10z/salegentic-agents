from pydantic import BaseModel
from typing import List, Optional


class UserContext(BaseModel):
    country: Optional[str] = None
    device: Optional[str] = None


class Message(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    query: str
    chat_history: Optional[List[Message]] = []
    context: Optional[UserContext] = None
