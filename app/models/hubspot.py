from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base


class Hubspot(Base):
    __tablename__ = "hubspots"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    id = Column(String, primary_key=True, nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    provider = Column(String, nullable=False, default="hubspot")
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    hubspot_portal_id = Column(String, nullable=False)
    account_name = Column(String)

    def __repr__(self):
        """Better representation for debugging"""
        return (f"Hubspot(id={self.id}, "
                f"workspace_id={self.workspace_id}, "
                f"hubspot_portal_id={self.hubspot_portal_id}, "
                f"expires_at={self.expires_at}, "
                f"is_active={self.is_active})")


from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class HubspotDeal:
    """Model representing a deal from Hubspot API"""
    id: str
    name: Optional[str] = None
    amount: Optional[float] = None
    deal_stage: Optional[str] = None
    close_date: Optional[datetime] = None
    pipeline: Optional[str] = None
    create_date: Optional[datetime] = None
    hubspot_owner_id: Optional[str] = None
    industry: Optional[str] = None
    contact_ids: List[str] = field(default_factory=list)
    company_ids: List[str] = field(default_factory=list)
    last_modified_date: Optional[datetime] = None


@dataclass
class HubspotPipelineStage:
    """Model representing a pipeline stage from Hubspot API"""
    id: str
    label: str
    display_order: int
    probability: Optional[float] = None
    closed_won: bool = False
    closed_lost: bool = False


@dataclass
class HubspotPipeline:
    """Model representing a pipeline from Hubspot API"""
    id: str
    label: str
    display_order: int
    stages: List[HubspotPipelineStage] = field(default_factory=list)


@dataclass
class HubspotContact:
    """Model representing a contact from Hubspot API"""
    id: str
    create_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None
    lifecycle_stage: Optional[str] = None
    email: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None


@dataclass
class HubspotEngagement:
    """Model representing an engagement from Hubspot API"""
    id: str
    type: str
    timestamp: Optional[datetime] = None
    # owner_id: Optional[str] = None
    # title: Optional[str] = None
    # contact_ids: List[str] = field(default_factory=list)
    # deal_ids: List[str] = field(default_factory=list)


@dataclass
class HubspotAnalyticsResult:
    """Model representing analytics data from Hubspot API"""
    start_date: datetime
    end_date: datetime
    deals_created: int = 0
    deals_closed_won: int = 0
    deals_closed_lost: int = 0
    revenue_generated: float = 0


@dataclass
class HubspotData:
    """Container for all Hubspot data fetched from the API"""
    deals: List[HubspotDeal] = field(default_factory=list)
    pipelines: List[HubspotPipeline] = field(default_factory=list)
    analytics: Optional[HubspotAnalyticsResult] = None
    contacts: List[HubspotContact] = field(default_factory=list)
    engagements: List[HubspotEngagement] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


from enum import Enum, auto


class HubspotDateField(Enum):
    LAST_MODIFIED_DATE = "hs_lastmodifieddate"
    CREATED_DATE = "createdate"
    CLOSED_DATE = "closedate"
