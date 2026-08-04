import logging

from app.core.config import settings
from neo4j import AsyncDriver, AsyncGraphDatabase

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver: AsyncDriver | None = None

    async def connect(self):
        try:
            self._driver = AsyncGraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )
            await self._driver.verify_connectivity()
            logger.info("Conectado a Neo4j exitosamente.")
        except Exception as e:
            logger.error(f"Error al conectar a Neo4j: {e}")
            raise e

    async def close(self):
        if self._driver is not None:
            await self._driver.close()
            logger.info("Conexión a Neo4j cerrada.")

    def get_driver(self) -> AsyncDriver:
        if self._driver is None:
            raise Exception("El driver de Neo4j no ha sido inicializado. Llame a connect() primero.")
        return self._driver

neo4j_client = Neo4jClient(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
)
