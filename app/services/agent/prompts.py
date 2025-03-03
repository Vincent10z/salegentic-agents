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