"""merge multiple heads

Revision ID: bb9b117e99d2
Revises: 20250302_deal_tables, 20250302_vector_db_tables
Create Date: 2025-03-04 07:22:39.018468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb9b117e99d2'
down_revision: Union[str, None] = ('20250302_deal_tables', '20250302_vector_db_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
