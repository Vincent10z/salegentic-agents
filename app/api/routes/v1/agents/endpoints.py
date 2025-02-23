from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.routes.v1.agents.request import UpdateMonitoringConfigRequest
from app.api.routes.v1.agents.response import HealthScoreResponse, RiskPatternsResponse, RecommendationsResponse, \
    MonitoringConfigResponse
from app.core.auth import get_current_user
from app.services.agent.agent_service import AgentService
from app.core.dependencies.services import get_agent_service


# Endpoints
async def analyze_workspace_health(
        workspace_id: str,
        force_refresh: bool = Query(False, description="Force a fresh analysis"),
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> HealthScoreResponse:
    """
    Analyze the overall health of a workspace, including engagement, pipeline, and risk metrics.
    """
    try:
        health_score = await agent_service.analyze_workspace_health(
            workspace_id=workspace_id,
            force_refresh=force_refresh
        )
        return HealthScoreResponse(**health_score.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_risk_patterns(
        workspace_id: str,
        timeframe_days: int = Query(30, ge=1, le=365),
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> RiskPatternsResponse:
    """
    Get identified risk patterns and potential issues for a workspace.
    """
    try:
        patterns = await agent_service.get_risk_patterns(
            workspace_id=workspace_id,
            timeframe=timedelta(days=timeframe_days)
        )
        return RiskPatternsResponse(**patterns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_recommendations(
        workspace_id: str,
        category: Optional[str] = Query(None, description="Filter recommendations by category"),
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> RecommendationsResponse:
    """
    Get AI-powered recommendations for improving workspace health.
    """
    try:
        recommendations = await agent_service.get_recommendations(
            workspace_id=workspace_id,
            category=category
        )
        return RecommendationsResponse(**recommendations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_at_risk_workspaces(
        risk_threshold: float = Query(0.7, ge=0, le=1),
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> List[HealthScoreResponse]:
    """
    Get a list of workspaces that are currently at risk.
    """
    try:
        at_risk = await agent_service.get_at_risk_workspaces(
            risk_threshold=risk_threshold
        )
        return [HealthScoreResponse(**workspace) for workspace in at_risk]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_monitoring_config(
        workspace_id: str,
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> MonitoringConfigResponse:
    """
    Get current monitoring configuration for a workspace.
    """
    try:
        config = await agent_service.get_monitoring_config(workspace_id)
        return MonitoringConfigResponse(**config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_monitoring_config(
        workspace_id: str,
        config: UpdateMonitoringConfigRequest,
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> MonitoringConfigResponse:
    """
    Update monitoring configuration for a workspace.
    """
    try:
        updated_config = await agent_service.update_monitoring_config(
            workspace_id=workspace_id,
            config_updates=config.dict(exclude_unset=True)
        )
        return MonitoringConfigResponse(**updated_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_health_trend(
        workspace_id: str,
        days: int = Query(30, ge=1, le=365),
        current_user: Dict = Depends(get_current_user),
        agent_service: AgentService = Depends(get_agent_service)
) -> List[HealthScoreResponse]:
    """
    Get historical health scores for trend analysis.
    """
    try:
        trend = await agent_service.get_health_trend(
            workspace_id=workspace_id,
            days=days
        )
        return [HealthScoreResponse(**score) for score in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
