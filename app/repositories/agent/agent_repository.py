from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.agent import AgentAnalysis, MonitoringConfig


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_analysis(self, analysis: AgentAnalysis) -> AgentAnalysis:
        """Save health analysis results."""
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_latest_analysis(self, workspace_id: str) -> Optional[AgentAnalysis]:
        """Get the most recent analysis for a workspace."""
        stmt = (
            select(AgentAnalysis)
            .where(AgentAnalysis.workspace_id == workspace_id)
            .order_by(AgentAnalysis.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_analysis_history(
            self,
            workspace_id: str,
            days: int = 30
    ) -> List[AgentAnalysis]:
        """Get historical analysis data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(AgentAnalysis)
            .where(
                AgentAnalysis.workspace_id == workspace_id,
                AgentAnalysis.created_at >= cutoff_date
            )
            .order_by(AgentAnalysis.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_monitoring_config(
            self,
            workspace_id: str
    ) -> Optional[MonitoringConfig]:
        """Get monitoring configuration for a workspace."""
        stmt = select(MonitoringConfig).where(
            MonitoringConfig.workspace_id == workspace_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_monitoring_config(
            self,
            workspace_id: str,
            updates: dict
    ) -> Optional[MonitoringConfig]:
        """Update monitoring configuration."""
        stmt = (
            update(MonitoringConfig)
            .where(MonitoringConfig.workspace_id == workspace_id)
            .values(**updates)
            .returning(MonitoringConfig)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def get_at_risk_analyses(
            self,
            risk_threshold: float = 0.7
    ) -> List[AgentAnalysis]:
        """Get analyses for workspaces at risk."""
        stmt = (
            select(AgentAnalysis)
            .where(AgentAnalysis.risk_score >= risk_threshold)
            .order_by(AgentAnalysis.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
