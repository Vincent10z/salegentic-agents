# app/models/account/plans.py
from sqlalchemy import Column, String, Text, TIMESTAMP
from app.models.base import Base
from datetime import datetime


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=datetime.utcnow)
    account_id = Column(Text, nullable=True)
