from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum

from app.services.agent.hubspot.account_health_agent.recommendations_engine import LLMRecommendationEngine


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskIndicator:
    name: str
    level: RiskLevel
    score: float
    details: Dict
    recommendations: List[str]


@dataclass
class AccountHealthScore:
    workspace_id: str
    overall_score: float
    risk_level: RiskLevel
    indicators: List[RiskIndicator]
    last_updated: datetime
    recommendations: List[str]


class AccountHealthAgent:
    def __init__(self, hubspot_service, analytics_processor, llm_client):
        self.hubspot_service = hubspot_service
        self.analytics_processor = analytics_processor
        self.recommendation_engine = LLMRecommendationEngine(llm_client)

        # Configure risk thresholds
        self.risk_thresholds = {
            "engagement_rate": {"low": 0.7, "medium": 0.5, "high": 0.3},
            "response_time": {"low": 24, "medium": 48, "high": 72},
            "deal_stagnation": {"low": 30, "medium": 45, "high": 60},
            "meeting_frequency": {"low": 14, "medium": 21, "high": 30}
        }

    async def analyze_account_health(self, workspace_id: str) -> AccountHealthScore:
        """Perform comprehensive account health analysis."""
        # Fetch analytics data
        analytics_data = await self.hubspot_service.get_analytics_data(
            workspace_id=workspace_id,
            start_date=datetime.now() - timedelta(days=90),
            include_contacts=True,
            include_engagements=True
        )

        # Get basic health indicators
        indicators = await self._analyze_basic_health_indicators(analytics_data)

        # Get AI-powered recommendations and analysis
        ai_analysis = await self.recommendation_engine.analyze_and_recommend(analytics_data)

        # Calculate overall health score
        overall_score = self._calculate_overall_score(indicators)
        risk_level = self._determine_risk_level(overall_score)

        # Combine basic recommendations with AI recommendations
        recommendations = self._merge_recommendations(
            self._generate_recommendations(indicators),
            ai_analysis.get('recommendations', [])
        )

        return AccountHealthScore(
            workspace_id=workspace_id,
            overall_score=overall_score,
            risk_level=risk_level,
            indicators=indicators,
            last_updated=datetime.now(),
            recommendations=recommendations,
            ai_analysis=ai_analysis  # Add AI analysis to the health score
        )

    async def _analyze_basic_health_indicators(self, analytics_data: Dict) -> List[RiskIndicator]:
        """Analyze basic health indicators."""
        indicators = []

        # Basic health checks
        engagement_indicator = await self._analyze_engagement_health(analytics_data)
        pipeline_indicator = await self._analyze_pipeline_health(analytics_data)
        response_indicator = await self._analyze_response_times(analytics_data)
        meeting_indicator = await self._analyze_meeting_frequency(analytics_data)

        indicators.extend([
            engagement_indicator,
            pipeline_indicator,
            response_indicator,
            meeting_indicator
        ])

        return indicators

    def _merge_recommendations(
            self,
            basic_recommendations: List[str],
            ai_recommendations: List[Dict]
    ) -> List[str]:
        """Merge and deduplicate recommendations."""
        # Convert AI recommendations to string format
        ai_rec_strings = [
            f"{rec['action']} (Priority: {rec['priority']}, Timeline: {rec['timeline']} days)"
            for rec in ai_recommendations
        ]

        # Combine and deduplicate
        all_recommendations = basic_recommendations + ai_rec_strings
        return list(dict.fromkeys(all_recommendations))

    async def _analyze_engagement_health(self, analytics_data: Dict) -> RiskIndicator:
        """Analyze engagement patterns and trends."""
        engagement_metrics = analytics_data.get('engagement_metrics', {})

        # Calculate engagement rate
        total_activities = engagement_metrics.get('total_activities', 0)
        time_period_days = 90  # Based on our analytics fetch
        daily_engagement = total_activities / time_period_days if time_period_days > 0 else 0

        # Compare with thresholds
        thresholds = self.risk_thresholds['engagement_rate']
        if daily_engagement >= thresholds['low']:
            level = RiskLevel.LOW
            score = 0.9
        elif daily_engagement >= thresholds['medium']:
            level = RiskLevel.MEDIUM
            score = 0.6
        else:
            level = RiskLevel.HIGH
            score = 0.3

        recommendations = [
            "Schedule regular check-in calls",
            "Implement engagement tracking",
            "Set up automated engagement reminders"
        ] if level != RiskLevel.LOW else []

        return RiskIndicator(
            name="engagement_health",
            level=level,
            score=score,
            details={
                "daily_engagement_rate": daily_engagement,
                "total_activities": total_activities
            },
            recommendations=recommendations
        )

    async def _analyze_pipeline_health(self, analytics_data: Dict) -> RiskIndicator:
        """Analyze deal pipeline health and stagnation."""
        pipeline_metrics = analytics_data.get('pipeline_metrics', {})

        # Check for stagnant deals
        stagnant_deals = []
        total_deals = len(pipeline_metrics.get('deals', []))

        for deal in pipeline_metrics.get('deals', []):
            days_in_stage = deal.get('days_in_stage', 0)
            if days_in_stage > self.risk_thresholds['deal_stagnation']['high']:
                stagnant_deals.append(deal)

        stagnation_rate = len(stagnant_deals) / total_deals if total_deals > 0 else 1

        # Determine risk level
        if stagnation_rate < 0.1:
            level = RiskLevel.LOW
            score = 0.9
        elif stagnation_rate < 0.3:
            level = RiskLevel.MEDIUM
            score = 0.6
        else:
            level = RiskLevel.HIGH
            score = 0.3

        return RiskIndicator(
            name="pipeline_health",
            level=level,
            score=score,
            details={
                "stagnant_deals_count": len(stagnant_deals),
                "total_deals": total_deals,
                "stagnation_rate": stagnation_rate
            },
            recommendations=self._get_pipeline_recommendations(level, stagnant_deals)
        )

    async def _analyze_response_times(self, analytics_data: Dict) -> RiskIndicator:
        """Analyze customer response times and patterns."""
        engagement_metrics = analytics_data.get('engagement_metrics', {})
        avg_response_time = engagement_metrics.get('avg_response_time', {})

        # Calculate average response time across all engagement types
        response_times = [
            time for time in avg_response_time.values()
            if isinstance(time, (int, float))
        ]
        avg_time = sum(response_times) / len(response_times) if response_times else 0

        # Determine risk level based on response time
        thresholds = self.risk_thresholds['response_time']
        if avg_time <= thresholds['low']:
            level = RiskLevel.LOW
            score = 0.9
        elif avg_time <= thresholds['medium']:
            level = RiskLevel.MEDIUM
            score = 0.6
        else:
            level = RiskLevel.HIGH
            score = 0.3

        return RiskIndicator(
            name="response_time",
            level=level,
            score=score,
            details={"average_response_time": avg_time},
            recommendations=self._get_response_time_recommendations(level)
        )

    def _calculate_overall_score(self, indicators: List[RiskIndicator]) -> float:
        """Calculate overall health score from all indicators."""
        weights = {
            "engagement_health": 0.3,
            "pipeline_health": 0.3,
            "response_time": 0.2,
            "meeting_frequency": 0.2
        }

        weighted_score = 0
        for indicator in indicators:
            weighted_score += indicator.score * weights.get(indicator.name, 0)

        return round(weighted_score, 2)

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine overall risk level based on score."""
        if score >= 0.7:
            return RiskLevel.LOW
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH

    def _generate_recommendations(self, indicators: List[RiskIndicator]) -> List[str]:
        """Generate prioritized list of recommendations."""
        all_recommendations = []
        for indicator in indicators:
            if indicator.level != RiskLevel.LOW:
                all_recommendations.extend(indicator.recommendations)

        # Prioritize and deduplicate recommendations
        return list(dict.fromkeys(all_recommendations))

    def _get_pipeline_recommendations(self, risk_level: RiskLevel, stagnant_deals: List[Dict]) -> List[str]:
        """Generate pipeline-specific recommendations."""
        recommendations = []
        if risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Immediate pipeline review required",
                "Schedule deal strategy sessions for stagnant opportunities",
                "Evaluate and update deal qualification criteria"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Review deals older than 45 days",
                "Update pipeline stages for accuracy",
                "Schedule follow-ups for key opportunities"
            ])
        return recommendations

    def _get_response_time_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Generate response time recommendations."""
        recommendations = []
        if risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Implement response time SLAs",
                "Set up automated response tracking",
                "Review customer communication workflow"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Monitor response times more closely",
                "Set up response time alerts",
                "Review team capacity and workload"
            ])
        return recommendations
