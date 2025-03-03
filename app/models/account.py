import uuid
from enum import Enum

from app.models.plan import Plan
from app.models.base import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL = "trial"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    active_plan_id = Column(String, ForeignKey(Plan.id))
    products_enabled = Column(Boolean, default=True)
    subscription_status = Column(String, nullable=False, default=AccountStatus.ACTIVE.value)
    plan_started_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
