import pytest
import pytest_asyncio
from app.core.config import settings
from app.main import app
from httpx import ASGITransport, AsyncClient
from testcontainers.community.neo4j import Neo4jContainer

@pytest.fixture(scope="session")
def neo4j_container():
    with Neo4jContainer("neo4j:5", password="testpassword") as neo4j:
        yield neo4j

@pytest.fixture(scope="session", autouse=True)
def set_env(neo4j_container):
    settings.NEO4J_URI = neo4j_container.get_connection_url()
    settings.NEO4J_USER = "neo4j"
    settings.NEO4J_PASSWORD = "testpassword"
    # Desactivar kafka temporalmente o mockearlo para las pruebas HTTP
    settings.KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
