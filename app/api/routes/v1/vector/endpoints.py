import json
from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, UploadFile, File, Form, Query, Path, status
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user
from app.services.vector.vector_service import VectorDBService
from app.core.dependencies.services import get_vector_service
from app.models.vector import DocumentStatus, DocumentType

from .response import (
    DocumentResponse,
    DocumentListResponse,
    DocumentContentResponse,
    SearchResponse,
    SearchHistoryResponse,
    transform_document_response,
    transform_document_list_response,
    transform_document_content_response,
    transform_search_response,
    transform_search_history_response
)
from .request import SearchDocumentsRequest


async def upload_document(
        workspace_id: str,
        file: UploadFile = File(..., description="Document file to upload"),
        metadata: Optional[str] = Form(None, description="Optional JSON metadata for the document"),
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> DocumentResponse:
    """Upload and process a document file."""
    try:
        custom_metadata = {}
        if metadata:
            try:
                custom_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid metadata JSON format"
                )

        document = await service.process_document(
            file=file,
            workspace_id=workspace_id,
            user_id=current_user["id"],
            custom_metadata=custom_metadata
        )

        return transform_document_response(document)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )


async def get_document(
        document_id: str,
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> DocumentResponse:
    """Get document metadata by ID."""
    document = await service.get_document_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return transform_document_response(document)


async def list_workspace_documents(
        workspace_id: str,
        status: Optional[DocumentStatus] = None,
        document_type: Optional[DocumentType] = None,
        limit: int = 100,
        offset: int = 0,
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> DocumentListResponse:
    """Get a list of documents for a workspace."""
    if status is not None and status not in DocumentStatus:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {status}"
        )

    if document_type is not None and document_type not in DocumentType:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type: {document_type}"
        )

    documents, total = await service.get_documents_by_workspace(
        workspace_id=workspace_id,
        status=status,
        document_type=document_type,
        limit=limit,
        offset=offset
    )

    return transform_document_list_response(
        documents=documents,
        total=total,
        limit=limit,
        offset=offset
    )


async def get_document_content(
        document_id: str,
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> DocumentContentResponse:
    """Get full content of a document."""
    try:
        result = await service.get_document_content(document_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document content: {str(e)}"
        )


async def delete_document(
        document_id: str,
        permanent: bool = Query(False, description="Whether to permanently delete the document and related data"),
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> None:
    """Delete a document by ID."""
    try:
        await service.delete_document(document_id, permanent=permanent)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )

async def search_documents(
        search_request: SearchDocumentsRequest,
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> SearchResponse:
    """Search for documents by content."""
    try:
        results = await service.search_documents(
            query=search_request.query,
            workspace_id=search_request.workspace_id,
            user_id=current_user["id"],
            limit=search_request.limit,
            similarity_threshold=search_request.similarity_threshold
        )

        return transform_search_response(
            results=results,
            query=search_request.query
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


async def search_documents_form(
        query: str,
        workspace_id: str,
        limit: int = Form(10, description="Maximum number of results to return"),
        similarity_threshold: float = Form(0.7, ge=0, le=1, description="Minimum similarity threshold (0-1)"),
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> SearchResponse:
    """Search for documents by content using form data."""
    try:
        results = await service.search_documents(
            query=query,
            workspace_id=workspace_id,
            user_id=current_user["id"],
            limit=limit,
            similarity_threshold=similarity_threshold
        )

        return transform_search_response(
            results=results,
            query=query
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


async def get_search_history(
        workspace_id: str,
        limit: int = 20,
        current_user: Dict = Depends(get_current_user),
        service: VectorDBService = Depends(get_vector_service)
) -> SearchHistoryResponse:
    """Get search history for a workspace."""
    try:
        searches = await service.get_recent_searches(
            workspace_id=workspace_id,
            limit=limit
        )

        return transform_search_history_response(searches)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history: {str(e)}"
        )