from fastapi import APIRouter, status
from . import endpoints
from .response import (
    AgentResponse,
    ConversationResponse,
    SyncResponse,
    ErrorResponse
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/agent",
    tags=["Agent"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Query the agent
router.add_api_route(
    path="/query",
    endpoint=endpoints.query_agent,
    methods=["POST"],
    summary="Query the agent",
    description="Process a natural language query using the agent and get a response",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
)

# Get conversation history
router.add_api_route(
    path="/conversations/{conversation_id}",
    endpoint=endpoints.get_conversation,
    methods=["GET"],
    summary="Get conversation history",
    description="Retrieve the history of a conversation including all messages",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
)

# Sync HubSpot data
router.add_api_route(
    path="/sync/hubspot",
    endpoint=endpoints.sync_hubspot_data,
    methods=["POST"],
    summary="Sync HubSpot data",
    description="Import and sync HubSpot deal data for analysis",
    response_model=SyncResponse,
    status_code=status.HTTP_200_OK,
)