"""add index for product cursor pagination

Revision ID: 22c41f06e22a
Revises: 6fc3ff65a5d6
Create Date: 2026-10-02 20:17:25.968820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22c41f06e22a'
down_revision: Union[str, Sequence[str], None] = '6fc3ff65a5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_products_created_at_id",
        "products",
        ["created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_created_at_id",
        table_name="products",
    )
