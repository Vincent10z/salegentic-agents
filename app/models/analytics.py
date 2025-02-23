from typing import Dict

from sqlalchemy import Column, String, DateTime, JSON

from app.models.base import Base


class AnalyticsResult(Base):
    """Store analytics results for quick retrieval"""
    __tablename__ = "analytics_results"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    model_version = Column(String, nullable=False)


class DealMetrics(Base):
    total_value: float
    avg_deal_size: float
    win_rate: float
    avg_sales_cycle: float
    deals_by_stage: Dict[str, int]
    monthly_trends: Dict[str, Dict[str, float]]


class EngagementMetrics(Base):
    total_activities: int
    activity_by_type: Dict[str, int]
    response_rates: Dict[str, float]
    avg_response_time: Dict[str, float]
    daily_activity_trends: Dict[str, int]
