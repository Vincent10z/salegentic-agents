from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
import uuid
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