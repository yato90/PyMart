"""optimize product cursor pagination

Revision ID: 6fc3ff65a5d6
Revises: 7ebe9ba7227e
Create Date: 2026-09-30 23:04:35.300539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fc3ff65a5d6'
down_revision: Union[str, Sequence[str], None] = '7ebe9ba7227e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "ix_products_category_created_at",
        table_name="products",
    )

    op.create_index(
        "ix_products_category_created_at_id",
        "products",
        ["category_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_category_created_at_id",
        table_name="products",
    )

    op.create_index(
        "ix_products_category_created_at",
        "products",
        ["category_id", "created_at"],
    )
