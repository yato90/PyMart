"""add processed events

Revision ID: 5f22dc941e9b
Revises: a920e98aba7d
Create Date: 2026-10-03 21:44:04.833935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f22dc941e9b'
down_revision: Union[str, Sequence[str], None] = 'a920e98aba7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("processed_events")
