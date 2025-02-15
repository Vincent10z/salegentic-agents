from fastapi import APIRouter, Depends
from app.services.agent_service import AgentService
from app.models.request import AgentRequest
from app.models.response import AgentResponse

router = APIRouter(prefix="/api/v1")


@router.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    response = await AgentService.process_query(request)
    return response
