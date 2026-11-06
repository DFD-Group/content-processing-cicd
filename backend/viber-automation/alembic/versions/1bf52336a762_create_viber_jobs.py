"""create_viber_jobs

Revision ID: 1bf52336a762
Revises:
Create Date: 2026-09-21 16:54:16.075125

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1bf52336a762"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "viber_jobs",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "plate_size",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "plate_sign",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "plate_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "dfd_order_number",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "customer_order_number",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "expedition_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "message_text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "viber_jobs",
        schema="app",
    )