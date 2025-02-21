"""initial schema

Revision ID: eabe7e9e7340
Revises: 
Create Date: 2025-02-22 00:11:16.790875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'eabe7e9e7340'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create plans table
    op.create_table('plans',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('account_id', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create accounts table
    op.create_table('accounts',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('active_plan_id', sa.String(), nullable=True),
                    sa.Column('products_enabled', sa.Boolean(), nullable=True, default=True),
                    sa.Column('subscription_status', sa.String(), nullable=True),
                    sa.Column('plan_started_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['active_plan_id'], ['plans.id'], name=op.f('fk_accounts_active_plan_id_plans')),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create users table
    op.create_table('users',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('first_name', sa.String(), nullable=True),
                    sa.Column('last_name', sa.String(), nullable=True),
                    sa.Column('account_id', sa.String(), nullable=True),
                    sa.Column('phone', sa.String(), nullable=True),
                    sa.Column('where_found_us', sa.String(), nullable=True),
                    sa.Column('account_role', sa.String(), nullable=True, default='standard'),
                    sa.Column('source', sa.String(), nullable=True, default='web'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_users_account_id_accounts')),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create hubspots table
    op.create_table('hubspots',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('user_id', sa.String(), nullable=False),
                    sa.Column('provider', sa.String(), nullable=False, default='hubspot'),
                    sa.Column('access_token', sa.String(), nullable=False),
                    sa.Column('refresh_token', sa.String(), nullable=False),
                    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
                    sa.Column('hubspot_portal_id', sa.String(), nullable=False),
                    sa.Column('account_name', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_hubspots_user_id_users')),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade() -> None:
    op.drop_table('hubspots')
    op.drop_table('users')
    op.drop_table('accounts')
    op.drop_table('plans')