from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = "20250302_deal_conversation_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "deal_snapshots",
        sa.Column("id", sa.String(), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("name", sa.String()),
        sa.Column("amount", sa.Float()),
        sa.Column("pipeline_id", sa.String()),
        sa.Column("stage_id", sa.String()),
        sa.Column("stage_name", sa.String()),
        sa.Column("owner_id", sa.String()),
        sa.Column("created_date", sa.DateTime(timezone=True)),
        sa.Column("last_modified_date", sa.DateTime(timezone=True)),
        sa.Column("close_date", sa.DateTime(timezone=True)),
        sa.Column("probability", sa.Float()),
        sa.Column("days_in_stage", sa.Integer()),
        sa.Column("days_in_pipeline", sa.Integer()),
        sa.Column("contact_ids", sa.JSON()),
        sa.Column("company_ids", sa.JSON()),
        sa.Column("properties", sa.JSON()),
        sa.Column("sync_date", sa.DateTime(timezone=True), nullable=False),
        sa.Index("idx_deal_workspace_external", "workspace_id", "external_id"),
        sa.Index("idx_deal_workspace_pipeline", "workspace_id", "pipeline_id"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("conversation_id", sa.String(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
    op.drop_table("deal_snapshots")
