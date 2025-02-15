from pydantic import BaseModel
from typing import List, Optional


class Source(BaseModel):
    title: str
    content: str
    url: Optional[str] = None


class AgentResponse(BaseModel):
    result: str
    sources: List[Source] = []
    needs_context: bool = False
    required_fields: List[str] = []
    confidence_score: Optional[float] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    requires_context: bool = False
    required_info: List[str] = []