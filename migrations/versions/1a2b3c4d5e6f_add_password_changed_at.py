"""add password_changed_at to users

Revision ID: 1a2b3c4d5e6f
Revises: d4f5af1c8b0e
Create Date: 2026-02-23

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1a2b3c4d5e6f"
down_revision = "d4f5af1c8b0e"
branch_labels = None
depends_on = None


def upgrade():
    # Add with server default so existing rows get populated.
    op.add_column(
        "users",
        sa.Column(
            "password_changed_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("users", "password_changed_at")
