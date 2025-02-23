from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel


class HealthScoreResponse(BaseModel):
    workspace_id: str
    overall_score: float
    risk_level: str
    indicators: List[Dict]
    recommendations: List[str]
    last_updated: datetime
    ai_analysis: Optional[Dict] = None


class RiskPatternsResponse(BaseModel):
    workspace_id: str
    patterns: List[Dict]
    risk_level: str
    recommendations: List[str]


class RecommendationsResponse(BaseModel):
    workspace_id: str
    recommendations: List[Dict]
    priority_actions: List[Dict]
    context: Dict


class MonitoringConfigResponse(BaseModel):
    workspace_id: str
    check_interval: int
    risk_threshold: str
    notification_settings: Dict
