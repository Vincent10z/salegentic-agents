from fastapi import Depends
from app.services.agent.agent_service import AgentService
from app.core.dependencies.services import get_agent_service


async def initialize_workspace_monitoring(
        workspace_id: str,
        agent_service: AgentService = Depends(get_agent_service)
):
    """Initialize monitoring for a new workspace."""
    return await agent_service.initialize_workspace_monitoring(workspace_id)


async def analyze_workspace_health(
        workspace_id: str,
        force_refresh: bool = False,
        agent_service: AgentService = Depends(get_agent_service)
):
    """Analyze workspace health."""
    return await agent_service.analyze_workspace_health(workspace_id, force_refresh)


async def get_at_risk_workspaces(
        agent_service: AgentService = Depends(get_agent_service)
):
    """Get list of workspaces that are at risk."""
    return await agent_service.get_at_risk_workspaces()


async def update_monitoring_config(
        workspace_id: str,
        config_updates: dict,
        agent_service: AgentService = Depends(get_agent_service)
):
    """Update monitoring configuration for a workspace."""
    return await agent_service.update_monitoring_config(workspace_id, config_updates)


async def get_health_trend(
        workspace_id: str,
        days: int = 30,
        agent_service: AgentService = Depends(get_agent_service)
):
    """Get health score trend for a workspace."""
    return await agent_service.get_health_trend(workspace_id, days)