from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import expression
from pgvector.sqlalchemy import Vector

from app.models.base import Base


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    DELETED = "deleted"
    ERROR = "error"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    TXT = "txt"
    HTML = "html"
    PPTX = "pptx"
    MD = "md"
    JSON = "json"
    OTHER = "other"


from app.core.id_generator.id_generator import (
    generate_document_id,
    generate_document_chunk_id,
    generate_document_embedding_id,
    generate_embedding_search_id
)


class DocumentStore(Base):
    """Store metadata about uploaded documents"""
    __tablename__ = "document_store"

    id = Column(String, primary_key=True, default=generate_document_id)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    document_metadata = Column(JSONB, nullable=False, server_default=expression.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)

    def __repr__(self):
        return f"<DocumentStore(id='{self.id}', filename='{self.filename}', status='{self.status}')>"


class DocumentChunk(Base):
    """Store chunks of text extracted from documents"""
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_document_chunk_id)
    document_id = Column(String, ForeignKey("document_store.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, nullable=False, server_default=expression.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_document_chunk_index', 'document_id', 'chunk_index', unique=True),
    )

    def __repr__(self):
        return f"<DocumentChunk(id='{self.id}', document_id='{self.document_id}', index={self.chunk_index})>"


class DocumentEmbedding(Base):
    """Store vector embeddings for document chunks"""
    __tablename__ = "document_embeddings"

    id = Column(String, primary_key=True, default=generate_document_embedding_id)
    chunk_id = Column(String, ForeignKey("document_chunks.id"), nullable=False, unique=True, index=True)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<DocumentEmbedding(id='{self.id}', chunk_id='{self.chunk_id}')>"


class EmbeddingSearch(Base):
    """Store search history and analytics"""
    __tablename__ = "embedding_searches"

    id = Column(String, primary_key=True, default=generate_embedding_search_id)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    search_metadata = Column(JSONB, nullable=False, server_default=expression.text("'{}'::jsonb"))

    def __repr__(self):
        return f"<EmbeddingSearch(id='{self.id}', query='{self.query[:20]}...')>"
