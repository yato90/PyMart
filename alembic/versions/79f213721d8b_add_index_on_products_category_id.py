"""add index on products category_id

Revision ID: 79f213721d8b
Revises: 28458051aed5
Create Date: 2026-09-30 22:32:23.546753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79f213721d8b'
down_revision: Union[str, Sequence[str], None] = '28458051aed5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_products_category_id",
        "products",
        ["category_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_category_id",
        table_name="products",
    )
