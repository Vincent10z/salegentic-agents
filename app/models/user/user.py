from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    account_id = Column(String, ForeignKey("accounts.id"))
    phone = Column(String)
    where_found_us = Column(String)
    account_role = Column(String, default='standard')
    source = Column(String, default='sf')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())