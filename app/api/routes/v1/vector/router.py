from fastapi import APIRouter, status
from . import endpoints
from .response import (
    DocumentResponse,
    DocumentListResponse,
    DocumentContentResponse,
    SearchResponse,
    SearchHistoryResponse,
    ErrorResponse
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/knowledge",
    tags=["Vector Database"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    }
)

# Document upload endpoint
router.add_api_route(
    path="/documents",
    endpoint=endpoints.upload_document,
    methods=["POST"],
    summary="Upload and process a document",
    description="Upload a document file, extract its text, create chunks, and generate embeddings",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)

# Get document metadata endpoint
router.add_api_route(
    path="/documents/{document_id}",
    endpoint=endpoints.get_document,
    methods=["GET"],
    summary="Get document details",
    description="Retrieve metadata for a specific document",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)

# Get documents by workspace_id
router.add_api_route(
    path="/documents",
    endpoint=endpoints.list_workspace_documents,
    methods=["GET"],
    summary="List documents in a workspace",
    description="Get a paginated list of documents for a workspace with optional filters",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
)

# Add this to app/api/routes/v1/knowledge/router.py
router.add_api_route(
    path="/documents/{document_id}",
    endpoint=endpoints.delete_document,
    methods=["DELETE"],
    summary="Delete a document",
    description="Mark a document as deleted and remove its chunks and embeddings from search results",
    response_model=None,
    status_code=status.HTTP_200_OK,
)

router.add_api_route(
    path="/documents/{document_id}/content",
    endpoint=endpoints.get_document_content,
    methods=["GET"],
    summary="Get document content",
    description="Retrieve the full content of a document by getting all its chunks",
    response_model=DocumentContentResponse,
    status_code=status.HTTP_200_OK,
)

# Search endpoints (JSON and form-based)
router.add_api_route(
    path="/search",
    endpoint=endpoints.search_documents,
    methods=["POST"],
    summary="Search documents (JSON)",
    description="Search for documents similar to the query using vector similarity (JSON body)",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)

router.add_api_route(
    path="/search-form",
    endpoint=endpoints.search_documents_form,
    methods=["POST"],
    summary="Search documents (Form)",
    description="Search for documents similar to the query using vector similarity (form data)",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)

router.add_api_route(
    path="/search-history",
    endpoint=endpoints.get_search_history,
    methods=["GET"],
    summary="Get search history",
    description="Retrieve recent searches for a workspace",
    response_model=SearchHistoryResponse,
    status_code=status.HTTP_200_OK,
)