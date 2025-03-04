from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Response model for document metadata"""
    id: str
    workspace_id: str
    filename: str
    document_type: str
    file_size: int
    status: str


class DocumentListResponse(BaseModel):
    """Response model for listing documents in a workspace"""
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int


class DocumentContentResponse(BaseModel):
    """Response model for document content"""
    document_id: str
    filename: str
    document_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[Dict[str, Any]]


class SearchResult(BaseModel):
    """Model for a single search result"""
    chunk_id: str
    content: str
    chunk_metadata: Dict[str, Any] = Field(default_factory=dict)
    document_id: str
    filename: str
    document_type: str
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    similarity: float


class SearchResponse(BaseModel):
    """Response model for search results"""
    results: List[SearchResult]
    query: str


class SearchHistoryItem(BaseModel):
    """Model for a single search history item"""
    id: str
    query: str
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchHistoryResponse(BaseModel):
    """Response model for search history"""
    searches: List[SearchHistoryItem]


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None
    context: Optional[dict] = None


# Transform functions to create response models from database models
def transform_document_response(document) -> DocumentResponse:
    """Transform a document model to a response model"""
    return DocumentResponse(
        id=document.id,
        workspace_id=document.workspace_id,
        filename=document.filename,
        document_type=document.document_type,
        file_size=document.file_size,
        processing_status=document.status.value,
    )


def transform_document_list_response(
        documents: List,
        total: int,
        limit: int,
        offset: int
) -> DocumentListResponse:
    """Transform a list of document models to a response model"""
    return DocumentListResponse(
        documents=[transform_document_response(doc) for doc in documents],
        total=total,
        limit=limit,
        offset=offset
    )


def transform_document_content_response(
        document_id: str,
        filename: str,
        document_type: str,
        metadata: Dict[str, Any],
        chunks: List[Dict[str, Any]]
) -> DocumentContentResponse:
    """Create a document content response"""
    return DocumentContentResponse(
        document_id=document_id,
        filename=filename,
        document_type=document_type,
        metadata=metadata or {},
        chunks=chunks
    )


def transform_search_response(
        results: List[Dict[str, Any]],
        query: str
) -> SearchResponse:
    """Transform search results to a response model"""
    search_results = [
        SearchResult(
            chunk_id=result["chunk_id"],
            content=result["content"],
            chunk_metadata=result["chunk_metadata"],
            document_id=result["document_id"],
            filename=result["filename"],
            document_type=result["document_type"],
            document_metadata=result["document_metadata"],
            similarity=result["similarity"]
        )
        for result in results
    ]

    return SearchResponse(
        results=search_results,
        query=query
    )


def transform_search_history_response(
        searches: List
) -> SearchHistoryResponse:
    """Transform search history to a response model"""
    search_items = [
        SearchHistoryItem(
            id=search.id,
            query=search.query,
            created_at=search.created_at.isoformat(),
            metadata=search.metadata or {}
        )
        for search in searches
    ]

    return SearchHistoryResponse(
        searches=search_items
    )