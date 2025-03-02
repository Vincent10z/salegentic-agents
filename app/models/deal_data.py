# app/models/deal_data.py
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON, func, Index
from app.models.base import Base
import uuid


class DealSnapshot(Base):
    """Stores imported deal data from CRM systems"""
    __tablename__ = "deal_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    external_id = Column(String, nullable=False)
    source = Column(String, nullable=False)

    # Deal properties
    name = Column(String)
    amount = Column(Float)
    pipeline_id = Column(String)
    stage_id = Column(String)
    stage_name = Column(String)
    owner_id = Column(String)

    # Important dates
    created_date = Column(DateTime(timezone=True))
    last_modified_date = Column(DateTime(timezone=True))
    close_date = Column(DateTime(timezone=True))

    # Additional data
    probability = Column(Float)
    days_in_stage = Column(Integer)
    days_in_pipeline = Column(Integer)

    # Contacts/Companies
    contact_ids = Column(JSON)
    company_ids = Column(JSON)

    # Metadata
    properties = Column(JSON)
    sync_date = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index('idx_deal_workspace_external', workspace_id, external_id),
        Index('idx_deal_workspace_pipeline', workspace_id, pipeline_id),
    )
