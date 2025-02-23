from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, func, Integer
from app.models.base import Base


class AgentAnalysis(Base):
    __tablename__ = "agent_analyses"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    analysis_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MonitoringConfig(Base):
    __tablename__ = "monitoring_configs"

    workspace_id = Column(String, ForeignKey("workspaces.id"), primary_key=True)
    check_interval = Column(Integer, default=24)
    risk_threshold = Column(Float, default=0.7)
    notification_settings = Column(JSON)
