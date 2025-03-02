# app/services/agent/tools/deal_analysis_tool.py
from typing import Dict, Any, List
from app.services.agent.tools.tool_registry import BaseTool
from app.repositories.hubspot.deal_repository import DealRepository
import json


class DealAnalysisTool(BaseTool):
    def __init__(self, deal_repository: DealRepository):
        self.deal_repository = deal_repository

    @property
    def name(self) -> str:
        return "analyze_deals"

    @property
    def description(self) -> str:
        return "Analyze CRM deals data. Input should specify analysis type (pipeline_health, conversion_rates, revenue_forecast, stalled_deals, or summary)."

    async def execute(
            self,
            workspace_id: str,
            user_id: str,
            query: str,
            conversation_id: str
    ) -> Dict[str, Any]:
        """Execute deal analysis based on the query"""

        # Parse the analysis type and parameters from the query
        try:
            # Try to parse JSON if provided
            params = json.loads(query)
            analysis_type = params.get("analysis_type", "summary")
        except:
            # Otherwise extract from text
            analysis_type = self._determine_analysis_type(query)

        # Get deals for the workspace
        deals = await self.deal_repository.get_deals_by_workspace(workspace_id)

        # Convert SQLAlchemy objects to dictionaries
        deal_dicts = []
        for deal in deals:
            deal_dict = {
                "id": deal.id,
                "external_id": deal.external_id,
                "name": deal.name,
                "amount": deal.amount,
                "pipeline_id": deal.pipeline_id,
                "stage_id": deal.stage_id,
                "stage_name": deal.stage_name,
                "owner_id": deal.owner_id,
                "created_date": deal.created_date.isoformat() if deal.created_date else None,
                "close_date": deal.close_date.isoformat() if deal.close_date else None,
                "probability": deal.probability,
                "days_in_stage": deal.days_in_stage,
                "days_in_pipeline": deal.days_in_pipeline
            }
            deal_dicts.append(deal_dict)

        # Run the appropriate analysis
        if analysis_type == "pipeline_health":
            result = self._analyze_pipeline_health(deal_dicts)
        elif analysis_type == "conversion_rates":
            result = self._analyze_conversion_rates(deal_dicts)
        elif analysis_type == "revenue_forecast":
            result = self._forecast_revenue(deal_dicts)
        elif analysis_type == "stalled_deals":
            result = self._identify_stalled_deals(deal_dicts)
        else:
            # Default to general deal summary
            result = self._generate_deal_summary(deal_dicts)

        # Return raw data for the agent to interpret
        return {
            "analysis_type": analysis_type,
            "deal_count": len(deals),
            "data": result["data"]
        }

    def _determine_analysis_type(self, query: str) -> str:
        """Determine what type of analysis is requested based on the query"""
        query = query.lower()

        if any(word in query for word in ["pipeline", "funnel", "stages"]):
            return "pipeline_health"
        elif any(word in query for word in ["conversion", "win rate", "close rate"]):
            return "conversion_rates"
        elif any(word in query for word in ["forecast", "predict", "revenue"]):
            return "revenue_forecast"
        elif any(word in query for word in ["stuck", "stalled", "bottleneck"]):
            return "stalled_deals"

        return "summary"

    def _analyze_pipeline_health(self, deals: List[Dict]) -> Dict[str, Any]:
        """Analyze deal distribution across pipeline stages"""
        # Group deals by pipeline and stage
        pipeline_data = {}
        for deal in deals:
            pipeline_id = deal["pipeline_id"]
            stage_id = deal["stage_id"]

            if not pipeline_id or not stage_id:
                continue

            if pipeline_id not in pipeline_data:
                pipeline_data[pipeline_id] = {"stages": {}, "total_value": 0, "count": 0}

            if stage_id not in pipeline_data[pipeline_id]["stages"]:
                pipeline_data[pipeline_id]["stages"][stage_id] = {
                    "name": deal["stage_name"],
                    "count": 0,
                    "value": 0
                }

            pipeline_data[pipeline_id]["stages"][stage_id]["count"] += 1
            pipeline_data[pipeline_id]["stages"][stage_id]["value"] += deal["amount"] or 0
            pipeline_data[pipeline_id]["total_value"] += deal["amount"] or 0
            pipeline_data[pipeline_id]["count"] += 1

        return {
            "data": pipeline_data
        }

    def _analyze_conversion_rates(self, deals: List[Dict]) -> Dict[str, Any]:
        """Analyze conversion rates between stages"""
        # Group deals by pipeline and calculate conversion rates
        pipeline_data = {}

        # First, organize deals by pipeline and stage
        for deal in deals:
            pipeline_id = deal.get("pipeline_id")
            stage_id = deal.get("stage_id")

            if not pipeline_id or not stage_id:
                continue

            if pipeline_id not in pipeline_data:
                pipeline_data[pipeline_id] = {"stages": {}, "total_deals": 0}

            if stage_id not in pipeline_data[pipeline_id]["stages"]:
                pipeline_data[pipeline_id]["stages"][stage_id] = {
                    "name": deal.get("stage_name"),
                    "count": 0
                }

            pipeline_data[pipeline_id]["stages"][stage_id]["count"] += 1
            pipeline_data[pipeline_id]["total_deals"] += 1

        # Calculate conversion rates between stages
        for pipeline_id, pipeline in pipeline_data.items():
            stages = sorted(
                pipeline["stages"].items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )

            # Assuming first stage has highest count
            first_stage_count = stages[0][1]["count"] if stages else 0

            for stage_id, stage_data in pipeline["stages"].items():
                if first_stage_count > 0:
                    stage_data["conversion_rate"] = (stage_data["count"] / first_stage_count) * 100
                else:
                    stage_data["conversion_rate"] = 0

        return {
            "data": pipeline_data
        }

    def _forecast_revenue(self, deals: List[Dict]) -> Dict[str, Any]:
        """Generate revenue forecast based on deal probabilities"""
        # Calculate expected revenue based on probability
        forecasted_revenue = 0
        weighted_by_stage = {}
        expected_close_dates = {}

        for deal in deals:
            amount = deal.get("amount") or 0
            probability = deal.get("probability") or 0
            stage_id = deal.get("stage_id")
            stage_name = deal.get("stage_name")
            close_date = deal.get("close_date")

            # Skip deals with no amount or probability
            if amount <= 0 or probability <= 0:
                continue

            # Calculate weighted revenue
            weighted_revenue = amount * (probability / 100)
            forecasted_revenue += weighted_revenue

            # Group by stage
            if stage_id:
                if stage_id not in weighted_by_stage:
                    weighted_by_stage[stage_id] = {
                        "name": stage_name,
                        "total": 0,
                        "count": 0
                    }
                weighted_by_stage[stage_id]["total"] += weighted_revenue
                weighted_by_stage[stage_id]["count"] += 1

            # Group by close date (month)
            if close_date:
                month = close_date[:7]  # YYYY-MM format
                if month not in expected_close_dates:
                    expected_close_dates[month] = {
                        "total": 0,
                        "count": 0
                    }
                expected_close_dates[month]["total"] += weighted_revenue
                expected_close_dates[month]["count"] += 1

        return {
            "data": {
                "forecasted_revenue": forecasted_revenue,
                "by_stage": weighted_by_stage,
                "by_month": expected_close_dates
            }
        }

    def _identify_stalled_deals(self, deals: List[Dict]) -> Dict[str, Any]:
        """Identify deals that have been stuck in a stage too long"""
        stalled_deals = []

        for deal in deals:
            days_in_stage = deal.get("days_in_stage") or 0

            # Consider deals stalled if in stage for more than 30 days
            if days_in_stage > 30:
                stalled_deals.append({
                    "id": deal.get("id"),
                    "name": deal.get("name"),
                    "amount": deal.get("amount"),
                    "stage_name": deal.get("stage_name"),
                    "days_in_stage": days_in_stage,
                    "probability": deal.get("probability")
                })

        # Sort by days in stage (descending)
        stalled_deals.sort(key=lambda x: x["days_in_stage"], reverse=True)

        return {
            "data": {
                "stalled_deals": stalled_deals,
                "count": len(stalled_deals)
            }
        }

    def _generate_deal_summary(self, deals: List[Dict]) -> Dict[str, Any]:
        """Generate a general summary of deals"""
        total_count = len(deals)
        total_value = sum(deal.get("amount") or 0 for deal in deals)
        avg_value = total_value / total_count if total_count > 0 else 0

        # Count by stage
        stages = {}
        pipelines = {}

        for deal in deals:
            pipeline_id = deal.get("pipeline_id")
            stage_id = deal.get("stage_id")
            stage_name = deal.get("stage_name")

            if stage_id:
                if stage_id not in stages:
                    stages[stage_id] = {
                        "name": stage_name,
                        "count": 0,
                        "value": 0
                    }
                stages[stage_id]["count"] += 1
                stages[stage_id]["value"] += deal.get("amount") or 0

            if pipeline_id:
                if pipeline_id not in pipelines:
                    pipelines[pipeline_id] = {
                        "count": 0,
                        "value": 0
                    }
                pipelines[pipeline_id]["count"] += 1
                pipelines[pipeline_id]["value"] += deal.get("amount") or 0

        return {
            "data": {
                "total_count": total_count,
                "total_value": total_value,
                "avg_deal_value": avg_value,
                "by_stage": stages,
                "by_pipeline": pipelines
            }
        }
