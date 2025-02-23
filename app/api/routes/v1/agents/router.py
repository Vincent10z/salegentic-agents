from fastapi import APIRouter
from app.api.routes.v1.agents import endpoints
from app.api.routes.v1.agents.response import (
    HealthScoreResponse,
    RiskPatternsResponse,
    RecommendationsResponse,
    MonitoringConfigResponse
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/agents",
    tags=["Agents"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    }
)

# Health Analysis Routes
router.add_api_route(
    path="/health",
    endpoint=endpoints.analyze_workspace_health,
    methods=["GET"],
    summary="Analyze Workspace Health",
    description="Get comprehensive health analysis for a workspace",
    response_model=HealthScoreResponse
)

router.add_api_route(
    path="/risks",
    endpoint=endpoints.get_risk_patterns,
    methods=["GET"],
    summary="Get Risk Patterns",
    description="Identify risk patterns and potential issues",
    response_model=RiskPatternsResponse
)

# Recommendations Routes
router.add_api_route(
    path="/recommendations",
    endpoint=endpoints.get_recommendations,
    methods=["GET"],
    summary="Get Recommendations",
    description="Get AI-powered recommendations for improvement",
    response_model=RecommendationsResponse
)

# Monitoring Routes
router.add_api_route(
    path="/at-risk",
    endpoint=endpoints.get_at_risk_workspaces,
    methods=["GET"],
    summary="Get At-Risk Workspaces",
    description="List workspaces currently at risk",
    response_model=list[HealthScoreResponse]
)

router.add_api_route(
    path="/config",
    endpoint=endpoints.get_monitoring_config,
    methods=["GET"],
    summary="Get Monitoring Config",
    description="Get current monitoring configuration",
    response_model=MonitoringConfigResponse
)

router.add_api_route(
    path="/monitoring/config",
    endpoint=endpoints.update_monitoring_config,
    methods=["PATCH"],
    summary="Update Monitoring Config",
    description="Update monitoring configuration",
    response_model=MonitoringConfigResponse
)

# Analytics Routes
router.add_api_route(
    path="/trend",
    endpoint=endpoints.get_health_trend,
    methods=["GET"],
    summary="Get Health Trend",
    description="Get historical health scores for trend analysis",
    response_model=list[HealthScoreResponse]
)