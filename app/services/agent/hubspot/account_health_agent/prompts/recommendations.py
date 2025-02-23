from typing import Dict, Any
from enum import Enum


class PromptTemplate(Enum):
    """Enum for different types of prompts"""
    SYSTEM = "system"
    RECOMMENDATIONS = "recommendations"
    RISK_ANALYSIS = "risk_analysis"
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"


class CRMPrompts:
    """Collection of prompts for CRM analysis"""

    SYSTEM_PROMPT = """
    You are an expert CRM analyst and business consultant. Your task is to analyze CRM data 
    and provide actionable recommendations. Focus on:
    1. Identifying risk patterns
    2. Suggesting specific, actionable steps
    3. Prioritizing recommendations based on impact and urgency
    4. Providing context-aware solutions
    
    Format your recommendations with clear steps, priorities, and expected outcomes.
    
    Account Context:
    - Industry: {industry}
    - Company Size: {company_size}
    - Current Health Score: {health_score}
    """

    RECOMMENDATIONS_PROMPT = """
    Based on the following CRM analysis data:
    {context}

    Provide specific, actionable recommendations to:
    1. Address identified risks
    2. Capitalize on opportunities
    3. Improve overall account health

    Consider these specific aspects:
    - Current Engagement Level: {engagement_level}
    - Deal Pipeline Status: {pipeline_status}
    - Recent Activity Trends: {activity_trends}
    - Key Stakeholder Involvement: {stakeholder_status}

    Format your response as a JSON array of recommendations, where each recommendation has:
    - priority (high/medium/low)
    - category (engagement/pipeline/relationship/process)
    - action (specific step to take)
    - expected_outcome
    - timeline (in days)
    - implementation_complexity (high/medium/low)
    - required_resources (array of strings)
    """

    RISK_ANALYSIS_PROMPT = """
    Analyze the following risk indicators for the account:
    {risk_data}

    Key Metrics:
    - Days Since Last Contact: {days_since_contact}
    - Deal Stagnation: {deal_stagnation}
    - Engagement Decline Rate: {engagement_decline}
    - Response Time Trends: {response_trends}

    Provide a detailed risk assessment focusing on:
    1. Immediate threats to account health
    2. Potential future risks
    3. Risk mitigation strategies
    4. Early warning indicators to monitor

    Format your response as a JSON object with:
    - risk_level (high/medium/low)
    - key_risks (array of risk factors)
    - mitigation_strategies (array of actionable steps)
    - monitoring_recommendations (array of metrics to track)
    """

    OPPORTUNITY_ANALYSIS_PROMPT = """
    Based on the following account data:
    {account_data}

    Current Product Usage:
    {product_usage}

    Similar Account Patterns:
    {similar_accounts}

    Identify growth opportunities considering:
    1. Product expansion possibilities
    2. Usage pattern optimization
    3. Engagement improvement areas
    4. Cross-sell/upsell potential

    Format your response as a JSON object with:
    - opportunities (array of specific opportunities)
    - priority_ranking (array of prioritized actions)
    - expected_impact (object with impact metrics)
    - implementation_plan (array of steps)
    """

    ENGAGEMENT_ANALYSIS_PROMPT = """
    Review the following engagement patterns:
    {engagement_data}

    Communication History:
    - Meeting Frequency: {meeting_frequency}
    - Email Response Rates: {email_metrics}
    - Key Contact Involvement: {contact_involvement}

    Analyze the engagement health focusing on:
    1. Communication effectiveness
    2. Stakeholder participation
    3. Engagement quality
    4. Relationship strength

    Format your response as a JSON object with:
    - engagement_score (0-100)
    - strength_factors (array of strong points)
    - weakness_factors (array of areas to improve)
    - engagement_recommendations (array of specific actions)
    """


class PromptManager:
    """Manager class for handling prompt templates and formatting"""

    @staticmethod
    def get_prompt(template: PromptTemplate, **kwargs) -> str:
        """
        Get a formatted prompt based on the template and provided variables.

        Args:
            template: The prompt template to use
            **kwargs: Variables to format the template with

        Returns:
            Formatted prompt string
        """
        prompt_map = {
            PromptTemplate.SYSTEM: CRMPrompts.SYSTEM_PROMPT,
            PromptTemplate.RECOMMENDATIONS: CRMPrompts.RECOMMENDATIONS_PROMPT,
            PromptTemplate.RISK_ANALYSIS: CRMPrompts.RISK_ANALYSIS_PROMPT,
            PromptTemplate.OPPORTUNITY_ANALYSIS: CRMPrompts.OPPORTUNITY_ANALYSIS_PROMPT,
            PromptTemplate.ENGAGEMENT_ANALYSIS: CRMPrompts.ENGAGEMENT_ANALYSIS_PROMPT
        }

        base_prompt = prompt_map.get(template)
        if not base_prompt:
            raise ValueError(f"Unknown prompt template: {template}")

        # Set default values for missing kwargs
        defaults = {
            'industry': 'Unknown',
            'company_size': 'Unknown',
            'health_score': 'N/A',
            'engagement_level': 'N/A',
            'pipeline_status': 'N/A',
            'activity_trends': 'N/A',
            'stakeholder_status': 'N/A',
            'context': '{}',
            'risk_data': '{}',
            'account_data': '{}',
            'product_usage': '{}',
            'similar_accounts': '{}',
            'engagement_data': '{}',
            'days_since_contact': 'N/A',
            'deal_stagnation': 'N/A',
            'engagement_decline': 'N/A',
            'response_trends': 'N/A',
            'meeting_frequency': 'N/A',
            'email_metrics': 'N/A',
            'contact_involvement': 'N/A'
        }

        # Update defaults with provided kwargs
        format_vars = {**defaults, **kwargs}

        try:
            return base_prompt.format(**format_vars)
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt template: {e}")

    @staticmethod
    def format_context(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analytics data into a structure suitable for prompt templates.

        Args:
            analytics_data: Raw analytics data

        Returns:
            Formatted context dictionary
        """
        return {
            'industry': analytics_data.get('account_details', {}).get('industry', 'Unknown'),
            'company_size': analytics_data.get('account_details', {}).get('company_size', 'Unknown'),
            'health_score': analytics_data.get('health_metrics', {}).get('overall_score', 'N/A'),
            'engagement_level': PromptManager._format_engagement_level(analytics_data),
            'pipeline_status': PromptManager._format_pipeline_status(analytics_data),
            'activity_trends': PromptManager._format_activity_trends(analytics_data),
            'stakeholder_status': PromptManager._format_stakeholder_status(analytics_data)
        }

    @staticmethod
    def _format_engagement_level(data: Dict) -> str:
        """Format engagement level data"""
        engagement = data.get('engagement_metrics', {})
        return f"Level: {engagement.get('level', 'Unknown')}, Trend: {engagement.get('trend', 'Stable')}"

    @staticmethod
    def _format_pipeline_status(data: Dict) -> str:
        """Format pipeline status data"""
        pipeline = data.get('pipeline_metrics', {})
        return f"Active Deals: {pipeline.get('active_deals', 0)}, Total Value: {pipeline.get('total_value', 0)}"

    @staticmethod
    def _format_activity_trends(data: Dict) -> str:
        """Format activity trends data"""
        trends = data.get('activity_trends', {})
        return f"30-day change: {trends.get('thirty_day_change', '0')}%"

    @staticmethod
    def _format_stakeholder_status(data: Dict) -> str:
        """Format stakeholder status data"""
        stakeholders = data.get('stakeholders', {})
        return f"Active: {stakeholders.get('active_count', 0)}, Key Decision Makers: {stakeholders.get('decision_makers', 0)}"
