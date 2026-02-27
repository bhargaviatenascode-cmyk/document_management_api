"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "document_status_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("old_status", sa.String(length=20), nullable=True),
        sa.Column("new_status", sa.String(length=20), nullable=False),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("document_status_history")
    op.drop_table("documents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
