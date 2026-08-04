import logging
from contextlib import asynccontextmanager

from app.api.endpoints import analytics, recipes
from app.core.config import settings
from app.core.neo4j_client import neo4j_client
from app.services.kafka_consumer import kafka_consumer_service
from fastapi import FastAPI

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Nutrition Graph Service...")
    await neo4j_client.connect()
    
    if settings.SEED_DB_ON_STARTUP:
        from app.core.seed import run_seed
        await run_seed(neo4j_client.get_driver())
        
    await kafka_consumer_service.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nutrition Graph Service...")
    await kafka_consumer_service.stop()
    await neo4j_client.close()

from nutrigraph_common.handlers import register_exception_handlers

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.router.lifespan_context = lifespan

app.include_router(recipes.router, prefix=f"{settings.API_V1_STR}/recipes", tags=["Recipes"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/admin/analytics", tags=["Analytics"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
