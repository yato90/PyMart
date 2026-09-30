"""add composite index for category products

Revision ID: 7ebe9ba7227e
Revises: 79f213721d8b
Create Date: 2026-09-30 22:46:50.625454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ebe9ba7227e'
down_revision: Union[str, Sequence[str], None] = '79f213721d8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_products_category_created_at",
        "products",
        ["category_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_category_created_at",
        table_name="products",
    )