"""Sprint-1 CP-2: Create projects tables — projects, project_units.

Constitutional:
- All tables include org_id for multi-tenant isolation
- PostgreSQL-compatible
- Links IAM to Execution

Revision ID: sprint1_projects
Revises: sprint1_iam
Create Date: 2026-07-10
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint1_projects"
down_revision: Union[str, None] = "sprint1_iam"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create projects tables with multi-tenant isolation."""

    # ─────────────────────────────────────────
    # projects — Core project entity
    # ─────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "org_id", sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            comment="Organization ID for multi-tenant isolation",
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_org_id", "projects", ["org_id"])

    # ─────────────────────────────────────────
    # project_units — Sub-units within a project
    # ─────────────────────────────────────────
    op.create_table(
        "project_units",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "org_id", sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "project_id", sa.Integer(),
            sa.ForeignKey("projects.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_units_org_id", "project_units", ["org_id"])
    op.create_index("ix_project_units_project_id", "project_units", ["project_id"])


def downgrade() -> None:
    """Drop projects tables in reverse dependency order."""
    op.drop_table("project_units")
    op.drop_table("projects")