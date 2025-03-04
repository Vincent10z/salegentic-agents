"""add default timestamps to tables

Revision ID: c33a67b822c7
Revises: bb9b117e99d2
Create Date: 2025-03-04 07:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c33a67b822c7'  # This should be the actual auto-generated ID
down_revision: Union[str, None] = 'bb9b117e99d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add defaults for conversation_messages table
    op.execute("""
        ALTER TABLE conversation_messages 
        ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP
    """)

    # Add defaults for conversations table
    op.execute("""
        ALTER TABLE conversations
        ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
        ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP
    """)

    # Add defaults for document_store table
    op.execute("""
        ALTER TABLE document_store
        ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP
    """)


def downgrade() -> None:
    # Remove defaults for document_store table
    op.execute("""
        ALTER TABLE document_store
        ALTER COLUMN updated_at DROP DEFAULT
    """)

    # Remove defaults for conversations table
    op.execute("""
        ALTER TABLE conversations
        ALTER COLUMN created_at DROP DEFAULT,
        ALTER COLUMN updated_at DROP DEFAULT
    """)

    # Remove defaults for conversation_messages table
    op.execute("""
        ALTER TABLE conversation_messages
        ALTER COLUMN created_at DROP DEFAULT
    """)