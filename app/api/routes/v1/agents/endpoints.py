# app/api/routes/v1/agent/endpoints.py
from typing import Dict, Optional
from fastapi import Depends, HTTPException, Path, Body
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user
from app.services.agent.agent_service import AgentService
from app.services.hubspot.data_sync_service import DataSyncService
from app.core.dependencies.services import get_agent_service, get_data_sync_service

from .response import (
    AgentResponse,
    ConversationResponse,
    SyncResponse,
    transform_agent_response,
    transform_conversation_response,
    # transform_sync_response
)
from .request import AgentQueryRequest


async def query_agent(
        workspace_id: str,
        query_request: AgentQueryRequest,
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Send a query to the agent and get a response"""
    try:
        result = await agent_service.process_query(
            workspace_id=workspace_id,
            user_id=query_request.user_id,
            query=query_request.query,
            conversation_id=query_request.conversation_id
        )

        return transform_agent_response(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


async def get_conversation(
        workspace_id: str,
        conversation_id: str,
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> ConversationResponse:
    """Get conversation history"""
    try:
        conversation = await agent_service.repository.get_conversation(conversation_id)
        if not conversation or conversation.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = await agent_service.repository.get_conversation_messages(conversation_id)

        return transform_conversation_response(
            conversation_id=conversation.id,
            workspace_id=conversation.workspace_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation: {str(e)}"
        )


async def sync_hubspot_data(
        workspace_id: str,
        current_user: Dict = Depends(get_current_user),
        crm_sync_service: DataSyncService = Depends(get_data_sync_service)
) -> SyncResponse:
    """Sync HubSpot deal data for a workspace"""
    try:
        result = await crm_sync_service.sync_hubspot_deals(workspace_id)
        return SyncResponse(
            deals_synced=result["deals_synced"],
            sync_date=result["sync_date"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing HubSpot data: {str(e)}"
        )