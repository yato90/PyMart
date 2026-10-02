import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from app.database.dependencies import get_db
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        "postgres:16",
        username="store",
        password="store",
        dbname="store_test",
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container):
    sync_url = postgres_container.get_connection_url()

    return sync_url.replace(
        "postgresql+psycopg2://",
        "postgresql+asyncpg://",
    )


@pytest.fixture(scope="session")
def run_migrations(database_url):
    settings.database_url = database_url

    config = Config("alembic.ini")

    command.upgrade(config, "head")

    return database_url


@pytest_asyncio.fixture
async def db_session(run_migrations):
    engine = create_async_engine(run_migrations)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()