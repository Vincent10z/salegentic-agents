from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.models.base import Base


class Workspace(Base):
    __tablename__ = 'workspaces'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    slug = Column(String, nullable=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Workspace(id='{self.id}', name='{self.name}', slug='{self.slug}')>"
