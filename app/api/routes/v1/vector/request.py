from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class SearchDocumentsRequest(BaseModel):
    """Request model for searching documents"""
    query: str = Field(..., description="The search query text")
    workspace_id: str = Field(..., description="ID of the workspace to search in")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results to return")
    similarity_threshold: float = Field(0.7, ge=0, le=1, description="Minimum similarity threshold (0-1)")


class DocumentMetadataRequest(BaseModel):
    """Request model for document metadata"""
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata for the document")