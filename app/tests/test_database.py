import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_migrations(db_session):
    result = await db_session.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
    )

    tables = {row[0] for row in result.all()}

    assert "products" in tables
    assert "categories" in tables
    assert "alembic_version" in tables