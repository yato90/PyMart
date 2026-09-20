"""add categories and product category

Revision ID: 28458051aed5
Revises: 42e454e21f52
Create Date: 2026-09-20 22:08:16.410536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28458051aed5'
down_revision: Union[str, Sequence[str], None] = '42e454e21f52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # 2. Create initial category for existing products
    op.execute(
        sa.text(
            """
            INSERT INTO categories (name, created_at, updated_at)
            VALUES ('Uncategorized', NOW(), NOW())
            """
        )
    )

    # 3. Add category_id temporarily as nullable
    op.add_column(
        "products",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )

    # 4. Assign existing products to Uncategorized
    op.execute(
        sa.text(
            """
            UPDATE products
            SET category_id = (
                SELECT id
                FROM categories
                WHERE name = 'Uncategorized'
            )
            """
        )
    )

    # 5. Make category_id required
    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 6. Add foreign key
    op.create_foreign_key(
        "fk_products_category_id",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_products_category_id",
        "products",
        type_="foreignkey",
    )

    op.drop_column(
        "products",
        "category_id",
    )

    op.drop_table(
        "categories",
    )
