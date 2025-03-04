"""Add vector database tables

Revision ID: 20250302_vector_db_tables
Revises: eabe7e9e7340
Create Date: 2025-03-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250302_vector_db_tables'
down_revision: Union[str, None] = 'eabe7e9e7340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Install pgvector extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # Create document_store table
    op.create_table(
        'document_store',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by_user_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('document_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id'], name=op.f('fk_document_store_uploaded_by_user_id_users')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_document_store_workspace_id_workspaces')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_document_store'))
    )
    op.create_index(op.f('ix_document_store_workspace_id'), 'document_store', ['workspace_id'], unique=False)

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['document_store.id'], name=op.f('fk_document_chunks_document_id_document_store')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_document_chunks'))
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index('idx_document_chunk_index', 'document_chunks', ['document_id', 'chunk_index'], unique=True)

    # Create document_embeddings table with vector column
    op.create_table(
        'document_embeddings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('chunk_id', sa.String(), nullable=False),
        # Using text directly for the vector column since SQLAlchemy doesn't support it natively
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], name=op.f('fk_document_embeddings_chunk_id_document_chunks')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_document_embeddings'))
    )
    op.create_index(op.f('ix_document_embeddings_chunk_id'), 'document_embeddings', ['chunk_id'], unique=True)

    # Alter the embedding column to use the vector type
    op.execute('ALTER TABLE document_embeddings ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536);')

    # Create embedding_searches table
    op.create_table(
        'embedding_searches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('search_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_embedding_searches_user_id_users')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_embedding_searches_workspace_id_workspaces')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_embedding_searches'))
    )
    op.create_index(op.f('ix_embedding_searches_workspace_id'), 'embedding_searches', ['workspace_id'], unique=False)

    # Create an index on the embedding column for faster cosine similarity searches
    op.execute('CREATE INDEX idx_document_embeddings_embedding ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);')


def downgrade() -> None:
    # Drop tables
    op.drop_table('embedding_searches')
    op.drop_table('document_embeddings')
    op.drop_table('document_chunks')
    op.drop_table('document_store')