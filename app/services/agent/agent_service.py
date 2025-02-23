from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.hubspot.hubspot_service import HubspotService
from app.services.agent.hubspot.account_health_agent.account_health import AccountHealthAgent, AccountHealthScore, \
    RiskLevel
from app.repositories.workspace.workspace import WorkspaceRepository


class AgentService:
    def __init__(
            self,
            db: AsyncSession = Depends(get_session),
            hubspot_service: HubspotService = Depends(),
            workspace_repository: WorkspaceRepository = None
    ):
        self.db = db
        self.hubspot_service = hubspot_service
        self.workspace_repository = workspace_repository or WorkspaceRepository(db)

        # Initialize agents
        self.account_health_agent = AccountHealthAgent(
            hubspot_service=hubspot_service,
            analytics_processor=hubspot_service.analytics_processor
        )

        # Configure default monitoring settings
        self.monitoring_config = {
            "health_check_interval": timedelta(days=1),
            "risk_notification_threshold": RiskLevel.MEDIUM,
            "max_concurrent_analyses": 10
        }

    async def initialize_workspace_monitoring(self, workspace_id: str) -> Dict:
        """Initialize monitoring for a new workspace."""
        try:
            # Verify workspace exists
            workspace = await self.workspace_repository.get_workspace(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")

            # Perform initial health analysis
            initial_health = await self.account_health_agent.analyze_account_health(workspace_id)

            # Store monitoring preferences and initial state
            monitoring_state = {
                "workspace_id": workspace_id,
                "last_analysis": datetime.now(),
                "next_analysis": datetime.now() + self.monitoring_config["health_check_interval"],
                "initial_health_score": initial_health.overall_score,
                "current_risk_level": initial_health.risk_level,
                "monitoring_active": True
            }

            # TODO: Store monitoring state in database

            return {
                "status": "initialized",
                "initial_health": initial_health,
                "next_analysis_scheduled": monitoring_state["next_analysis"]
            }

        except Exception as e:
            # Log the error
            print(f"Error initializing workspace monitoring: {str(e)}")
            raise

    async def analyze_workspace_health(
            self,
            workspace_id: str,
            force_refresh: bool = False
    ) -> AccountHealthScore:
        """
        Analyze workspace health, using cached results if available and recent.
        """
        try:
            # Check if we have recent analysis results
            cached_analysis = await self._get_cached_analysis(workspace_id)

            if cached_analysis and not force_refresh:
                if datetime.now() - cached_analysis.last_updated < self.monitoring_config["health_check_interval"]:
                    return cached_analysis

            # Perform fresh analysis
            health_score = await self.account_health_agent.analyze_account_health(workspace_id)

            # Cache the results
            await self._cache_analysis_results(workspace_id, health_score)

            # Check if notification needed
            if health_score.risk_level >= self.monitoring_config["risk_notification_threshold"]:
                await self._handle_risk_notification(workspace_id, health_score)

            return health_score

        except Exception as e:
            # Log the error
            print(f"Error analyzing workspace health: {str(e)}")
            raise

    async def get_at_risk_workspaces(self) -> List[Dict]:
        """
        Identify workspaces that are at risk based on recent analyses.
        """
        try:
            at_risk_workspaces = []
            workspaces = await self.workspace_repository.get_workspaces()

            for workspace in workspaces:
                health_score = await self.analyze_workspace_health(workspace.id)

                if health_score.risk_level >= RiskLevel.MEDIUM:
                    at_risk_workspaces.append({
                        "workspace_id": workspace.id,
                        "workspace_name": workspace.name,
                        "risk_level": health_score.risk_level,
                        "health_score": health_score.overall_score,
                        "key_indicators": [
                            {
                                "name": indicator.name,
                                "level": indicator.level,
                                "score": indicator.score
                            }
                            for indicator in health_score.indicators
                            if indicator.level >= RiskLevel.MEDIUM
                        ],
                        "top_recommendations": health_score.recommendations[:3]
                    })

            return at_risk_workspaces

        except Exception as e:
            # Log the error
            print(f"Error getting at-risk workspaces: {str(e)}")
            raise

    async def update_monitoring_config(
            self,
            workspace_id: str,
            config_updates: Dict
    ) -> Dict:
        """
        Update monitoring configuration for a workspace.
        """
        try:
            # Validate and update monitoring settings
            valid_updates = {}

            if "health_check_interval" in config_updates:
                interval_days = config_updates["health_check_interval"]
                valid_updates["health_check_interval"] = timedelta(days=interval_days)

            if "risk_notification_threshold" in config_updates:
                threshold = config_updates["risk_notification_threshold"]
                if threshold in [level.value for level in RiskLevel]:
                    valid_updates["risk_notification_threshold"] = RiskLevel(threshold)

            # Update workspace-specific monitoring config
            # TODO: Store in database

            return {
                "workspace_id": workspace_id,
                "updated_config": valid_updates,
                "status": "updated"
            }

        except Exception as e:
            # Log the error
            print(f"Error updating monitoring config: {str(e)}")
            raise

    async def get_health_trend(
            self,
            workspace_id: str,
            days: int = 30
    ) -> List[Dict]:
        """
        Get health score trend for a workspace over time.
        """
        try:
            # TODO: Implement retrieval of historical health scores
            # This would require storing health scores in a database

            return []

        except Exception as e:
            # Log the error
            print(f"Error getting health trend: {str(e)}")
            raise

    async def _get_cached_analysis(
            self,
            workspace_id: str
    ) -> Optional[AccountHealthScore]:
        """
        Retrieve cached analysis results if available.
        """
        # TODO: Implement cache retrieval
        return None

    async def _cache_analysis_results(
            self,
            workspace_id: str,
            health_score: AccountHealthScore
    ):
        """
        Cache analysis results for future use.
        """
        # TODO: Implement caching
        pass

    async def _handle_risk_notification(
            self,
            workspace_id: str,
            health_score: AccountHealthScore
    ):
        """
        Handle notifications for high-risk accounts.
        """
        # TODO: Implement notification system
        notification_data = {
            "workspace_id": workspace_id,
            "risk_level": health_score.risk_level,
            "score": health_score.overall_score,
            "key_issues": [
                indicator.name
                for indicator in health_score.indicators
                if indicator.level >= RiskLevel.MEDIUM
            ],
            "recommendations": health_score.recommendations
        }

        # Log notification for now
        print(f"Risk notification: {notification_data}")
