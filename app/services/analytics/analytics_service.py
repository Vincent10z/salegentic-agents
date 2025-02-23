from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, List
from collections import defaultdict

from app.models.analytics_agent import (
    AnalyticsAgentInput,
    DealMetricsModel,
    PipelineMetricsModel,
    DealTrendsModel,
    EngagementMetricsModel,
    ContactMetricsModel,
    RiskMetricsModel,
    OpportunityMetricsModel,
    DealStage,
    EngagementType
)


class AnalyticsProcessor:
    @staticmethod
    async def prepare_analytics_agent_input(
            workspace_id: str,
            deals_data: dict,
            pipelines_data: dict,
            engagements_data: Optional[dict] = None,
            contacts_data: Optional[dict] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> AnalyticsAgentInput:
        """
        Process raw Hubspot data into structured input for the analytics agent.
        """
        # Process core deal metrics
        deal_metrics = await AnalyticsProcessor._process_deal_metrics(deals_data)

        # Process pipeline metrics
        pipeline_metrics = await AnalyticsProcessor._process_pipeline_metrics(
            deals_data,
            pipelines_data
        )

        # Process deal trends
        deal_trends = await AnalyticsProcessor._process_deal_trends(
            deals_data,
            start_date,
            end_date
        )

        # Process engagement metrics if available
        engagement_metrics = None
        if engagements_data:
            engagement_metrics = await AnalyticsProcessor._process_engagement_metrics(
                engagements_data,
                start_date,
                end_date
            )

        # Process contact metrics if available
        contact_metrics = None
        if contacts_data:
            contact_metrics = await AnalyticsProcessor._process_contact_metrics(
                contacts_data,
                engagements_data
            )

        # Generate risk metrics
        risk_metrics = await AnalyticsProcessor._generate_risk_metrics(
            deals_data,
            engagements_data
        )

        # Generate opportunity metrics
        opportunity_metrics = await AnalyticsProcessor._generate_opportunity_metrics(
            deals_data,
            contacts_data,
            engagement_metrics
        )

        # Create time period string
        time_period = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}" if start_date and end_date else "all_time"

        return AnalyticsAgentInput(
            workspace_id=workspace_id,
            time_period=time_period,
            deal_metrics=deal_metrics,
            pipeline_metrics=pipeline_metrics,
            deal_trends=deal_trends,
            engagement_metrics=engagement_metrics,
            contact_metrics=contact_metrics,
            risk_metrics=risk_metrics,
            opportunity_metrics=opportunity_metrics
        )

    @staticmethod
    async def _process_deal_metrics(deals_data: dict) -> DealMetricsModel:
        """Process raw deal data into deal metrics."""
        deals = deals_data.get('results', [])

        total_value = sum(float(deal.get('amount', 0)) for deal in deals)
        total_deals = len(deals)
        active_deals = len([d for d in deals if d.get('dealstage') not in
                            [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]])

        won_deals = [d for d in deals if d.get('dealstage') == DealStage.CLOSED_WON]
        win_rate = len(won_deals) / total_deals if total_deals > 0 else 0

        avg_sales_cycle = AnalyticsProcessor._calculate_avg_sales_cycle(deals)

        return DealMetricsModel(
            total_value=total_value,
            average_deal_size=total_value / total_deals if total_deals > 0 else 0,
            win_rate=win_rate,
            average_sales_cycle_days=avg_sales_cycle,
            total_deals=total_deals,
            active_deals=active_deals
        )

    @staticmethod
    async def _process_pipeline_metrics(
            deals_data: dict,
            pipelines_data: dict
    ) -> PipelineMetricsModel:
        """Process pipeline data into pipeline metrics."""
        deals = deals_data.get('results', [])

        # Count deals in each stage
        stages = defaultdict(int)
        stage_values = defaultdict(float)
        stage_durations = defaultdict(list)

        for deal in deals:
            stage = DealStage(deal.get('dealstage', 'unknown'))
            stages[stage] += 1
            stage_values[stage] += float(deal.get('amount', 0))

            # Calculate time in current stage
            if deal.get('properties', {}).get('dealstage_timestamps'):
                timestamps = deal['properties']['dealstage_timestamps']
                stage_durations[stage].append(
                    AnalyticsProcessor._calculate_stage_duration(timestamps)
                )

        # Calculate conversion rates between stages
        conversion_rates = AnalyticsProcessor._calculate_stage_conversion_rates(
            stages,
            pipelines_data
        )

        # Calculate average time in each stage
        avg_time_in_stage = {
            stage: sum(durations) / len(durations) if durations else 0
            for stage, durations in stage_durations.items()
        }

        return PipelineMetricsModel(
            stages=dict(stages),
            conversion_rates=conversion_rates,
            avg_time_in_stage=avg_time_in_stage,
            stage_value=dict(stage_values)
        )

    @staticmethod
    async def _process_deal_trends(
            deals_data: dict,
            start_date: Optional[datetime],
            end_date: Optional[datetime]
    ) -> DealTrendsModel:
        """Process deal data into trend metrics."""
        deals = deals_data.get('results', [])

        # Group deals by month
        monthly_deals = defaultdict(list)
        for deal in deals:
            if deal.get('createdate'):
                date = datetime.fromtimestamp(deal['createdate'] / 1000, timezone.utc)
                if (not start_date or date >= start_date) and (not end_date or date <= end_date):
                    month_key = date.strftime('%Y-%m')
                    monthly_deals[month_key].append(deal)

        # Calculate monthly metrics
        monthly_counts = {
            month: len(deals)
            for month, deals in monthly_deals.items()
        }

        monthly_values = {
            month: sum(float(deal.get('amount', 0)) for deal in deals)
            for month, deals in monthly_deals.items()
        }

        # Calculate growth rate
        months = sorted(monthly_counts.keys())
        if len(months) >= 2:
            current = monthly_values[months[-1]]
            previous = monthly_values[months[-2]]
            growth_rate = ((current - previous) / previous) if previous > 0 else 0
        else:
            growth_rate = 0.0

        # Identify seasonal patterns (simple 3-month rolling average)
        seasonal_patterns = {}
        if len(months) >= 3:
            for i in range(len(months) - 2):
                period = months[i:i+3]
                avg_value = sum(monthly_values[m] for m in period) / 3
                seasonal_patterns[period[-1]] = avg_value

        return DealTrendsModel(
            monthly_counts=monthly_counts,
            monthly_values=monthly_values,
            growth_rate=growth_rate,
            seasonal_patterns=seasonal_patterns
        )

    @staticmethod
    async def _process_engagement_metrics(
            engagements_data: dict,
            start_date: Optional[datetime],
            end_date: Optional[datetime]
    ) -> EngagementMetricsModel:
        """Process engagement data into metrics."""
        engagements = engagements_data.get('results', [])

        # Filter by date range if provided
        filtered_engagements = [
            eng for eng in engagements
            if AnalyticsProcessor._is_in_date_range(
                eng.get('createdAt'),
                start_date,
                end_date
            )
        ]

        # Count activities by type
        activity_by_type = defaultdict(int)
        for eng in filtered_engagements:
            eng_type = EngagementType(eng.get('type', 'unknown'))
            activity_by_type[eng_type] += 1

        # Calculate response rates and times
        response_rates = {}
        response_times = {}
        for eng_type in EngagementType:
            type_engagements = [e for e in filtered_engagements if e.get('type') == eng_type]
            if type_engagements:
                responses = [e for e in type_engagements if e.get('responded_at')]
                response_rates[eng_type] = len(responses) / len(type_engagements)

                if responses:
                    avg_response_time = sum(
                        (e['responded_at'] - e['createdAt']).total_seconds() / 3600
                        for e in responses
                    ) / len(responses)
                    response_times[eng_type] = avg_response_time

        # Calculate effectiveness score (simple weighted average)
        total_activities = len(filtered_engagements)
        if total_activities > 0:
            weighted_responses = sum(
                response_rates.get(eng_type, 0) * count
                for eng_type, count in activity_by_type.items()
            )
            effectiveness = weighted_responses / total_activities
        else:
            effectiveness = 0.0

        return EngagementMetricsModel(
            total_activities=total_activities,
            activity_by_type=dict(activity_by_type),
            response_rates=response_rates,
            avg_response_time=response_times,
            engagement_effectiveness=effectiveness
        )

    @staticmethod
    async def _process_contact_metrics(
            contacts_data: dict,
            engagements_data: Optional[dict]
    ) -> ContactMetricsModel:
        """Process contact data into metrics."""
        contacts = contacts_data.get('results', [])

        total_contacts = len(contacts)
        active_contacts = len([
            c for c in contacts
            if c.get('lastmodifieddate') and
               (datetime.now(timezone.utc) - datetime.fromtimestamp(c['lastmodifieddate'] / 1000, timezone.utc)).days <= 90
        ])

        # Calculate engagement rate
        if engagements_data:
            engaged_contacts = set(
                eng['contact_id']
                for eng in engagements_data.get('results', [])
                if eng.get('contact_id')
            )
            engagement_rate = len(engaged_contacts) / total_contacts if total_contacts > 0 else 0
        else:
            engagement_rate = 0.0

        # Calculate lead conversion
        converted_contacts = len([
            c for c in contacts
            if c.get('lifecyclestage') == 'customer'
        ])
        lead_conversion_rate = converted_contacts / total_contacts if total_contacts > 0 else 0

        # Calculate average interactions
        if engagements_data:
            interactions_by_contact = defaultdict(int)
            for eng in engagements_data.get('results', []):
                if eng.get('contact_id'):
                    interactions_by_contact[eng['contact_id']] += 1

            avg_interactions = (
                sum(interactions_by_contact.values()) / total_contacts
                if total_contacts > 0 else 0
            )
        else:
            avg_interactions = 0.0

        return ContactMetricsModel(
            total_contacts=total_contacts,
            active_contacts=active_contacts,
            engagement_rate=engagement_rate,
            lead_conversion_rate=lead_conversion_rate,
            avg_interactions_per_contact=avg_interactions
        )

    @staticmethod
    async def _generate_risk_metrics(
            deals_data: dict,
            engagements_data: Optional[dict]
    ) -> RiskMetricsModel:
        """Generate risk metrics from deal and engagement data."""
        deals = deals_data.get('results', [])

        risk_factors = {
            'no_recent_engagement': 0.4,
            'long_in_stage': 0.3,
            'missed_close_date': 0.2,
            'low_engagement_rate': 0.1
        }

        at_risk_deals = []
        for deal in deals:
            risk_score = 0

            # Check for recent engagement
            if engagements_data:
                recent_engagement = any(
                    eng for eng in engagements_data.get('results', [])
                    if eng.get('deal_id') == deal['id'] and
                    (datetime.now(timezone.utc) - datetime.fromtimestamp(eng['createdAt'] / 1000, timezone.utc)).days <= 30
                )
                if not recent_engagement:
                    risk_score += risk_factors['no_recent_engagement']

            # Check time in current stage
            if deal.get('properties', {}).get('dealstage_timestamps'):
                time_in_stage = AnalyticsProcessor._calculate_stage_duration(
                    deal['properties']['dealstage_timestamps']
                )
                if time_in_stage > 30:  # More than 30 days in stage
                    risk_score += risk_factors['long_in_stage']

            # Check if past expected close date
            if deal.get('closedate'):
                expected_close = datetime.fromtimestamp(deal['closedate'] / 1000, timezone.utc)
                if datetime.now(timezone.utc) > expected_close:
                    risk_score += risk_factors['missed_close_date']

            # Check engagement rate
            if engagements_data:
                deal_engagements = [
                    eng for eng in engagements_data.get('results', [])
                    if eng.get('deal_id') == deal['id']
                ]
                if len(deal_engagements) < 3:  # Less than 3 engagements
                    risk_score += risk_factors['low_engagement_rate']

            if risk_score >= 0.5:  # Risk threshold
                at_risk_deals.append(deal['id'])

        recommended_actions = [
            "Schedule follow-up calls with deals showing no recent engagement",
            "Review and update sales stages for deals stuck in current stage",
            "Reassess close dates for at-risk deals",
            "Increase engagement activities for low-interaction deals"
        ]

        return RiskMetricsModel(
            at_risk_deals=at_risk_deals,
            risk_factors=risk_factors,
            risk_score=len(at_risk_deals) / len(deals) if deals else 0.0,
            recommended_actions=recommended_actions
        )

    @staticmethod
    async def _generate_opportunity_metrics(
            deals_data: dict,
            contacts_data: Optional[dict],
            engagement_metrics: Optional[EngagementMetricsModel]
    ) -> OpportunityMetricsModel:
        """Generate opportunity metrics from available data."""
        deals = deals_data.get('results', [])

        # Identify high-value prospects
        high_value_prospects = []
        if contacts_data:
            contacts = contacts_data.get('results', [])
            for contact in contacts:
                # Consider factors like engagement level, company size, etc.
                if (contact.get('lifecyclestage') == 'opportunity' and
                        contact.get('company_size', '').lower() in ['enterprise', 'large']):
                    high_value_prospects.append(contact['id'])

        # Identify upsell opportunities
        upsell_opportunities = []
        for deal in deals:
            if (deal.get('dealstage') == DealStage.CLOSED_WON and
                    float(deal.get('amount', 0)) < 50000):  # Example threshold
                upsell_opportunities.append(deal['id'])

        # Identify growth segments
        growth_segments = {}
        if deals:
            # Group deals by industry or other relevant segment
            segments = defaultdict(list)
            for deal in deals:
                segment = deal.get('industry', 'unknown')
                segments[segment].append(float(deal.get('amount', 0)))

            # Calculate growth rate for each segment
            for segment, amounts in segments.items():
                if len(amounts) >= 2:
                    growth_rate = (amounts[-1] - amounts[0]) / amounts[0] if amounts[0] > 0 else 0
                    growth_segments[segment] = growth_rate

        # Generate recommended focus areas
        recommended_focus_areas = [
            "Enterprise clients in high-growth segments",
            "Existing customers with upsell potential",
            "Highly engaged prospects",
            "Industries with proven success rates"
        ]

        return OpportunityMetricsModel(
            high_value_prospects=high_value_prospects,
            upsell_opportunities=upsell_opportunities,
            growth_segments=growth_segments,
            recommended_focus_areas=recommended_focus_areas
        )

    @staticmethod
    def _calculate_avg_sales_cycle(deals: List[Dict]) -> float:
        """Calculate average time from creation to close in days."""
        cycles = []
        for deal in deals:
            if deal.get('closedate') and deal.get('createdate'):
                close_date = datetime.fromtimestamp(deal['closedate'] / 1000, timezone.utc)
                create_date = datetime.fromtimestamp(deal['createdate'] / 1000, timezone.utc)
                cycles.append((close_date - create_date).days)

        return sum(cycles) / len(cycles) if cycles else 0

    @staticmethod
    def _calculate_stage_duration(timestamps: Dict) -> float:
        """Calculate the duration in the current stage in days."""
        if not timestamps:
            return 0

        current_stage_start = datetime.fromtimestamp(
            timestamps.get('current_stage_start', 0) / 1000,
            timezone.utc
        )
        return (datetime.now(timezone.utc) - current_stage_start).days

    @staticmethod
    def _calculate_stage_conversion_rates(
            stages: Dict[DealStage, int],
            pipelines_data: Dict
    ) -> Dict[DealStage, float]:
        """Calculate conversion rates between pipeline stages."""
        conversion_rates = {}
        stage_order = [
            DealStage.APPOINTMENT_SCHEDULED,
            DealStage.QUALIFIED_TO_BUY,
            DealStage.PRESENTATION_SCHEDULED,
            DealStage.DECISION_MAKER_BOUGHT_IN,
            DealStage.CONTRACT_SENT,
            DealStage.CLOSED_WON
        ]

        for i in range(len(stage_order) - 1):
            current_stage = stage_order[i]
            next_stage = stage_order[i + 1]

            current_count = stages.get(current_stage, 0)
            next_count = stages.get(next_stage, 0)

            conversion_rates[current_stage] = (
                next_count / current_count if current_count > 0 else 0
            )

        return conversion_rates

    @staticmethod
    def _is_in_date_range(
            timestamp: Optional[int],
            start_date: Optional[datetime],
            end_date: Optional[datetime]
    ) -> bool:
        """Check if a timestamp falls within the given date range."""
        if not timestamp:
            return False

        date = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
        return (not start_date or date >= start_date) and (not end_date or date <= end_date)