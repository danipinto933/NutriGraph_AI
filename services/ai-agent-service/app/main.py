import logging
from contextlib import asynccontextmanager

import httpx
from app.api.endpoints import analytics, chat
from app.core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nutrigraph_common.handlers import register_exception_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.core.client import http_client
from app.models.chat_repository import chat_repository
from app.services.kafka_service import kafka_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Agent Service")
    try:
        await chat_repository.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j on startup: {e}")

    try:
        await kafka_service.start()
    except Exception as e:
        logger.warning(f"Failed to start Kafka consumer on startup: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Agent Service")
    try:
        await kafka_service.stop()
    except Exception as e:
        logger.warning(f"Error stopping Kafka consumer: {e}")

    try:
        await chat_repository.close()
    except Exception as e:
        logger.warning(f"Error closing Neo4j connection: {e}")

    try:
        await http_client.aclose()
    except Exception as e:
        logger.warning(f"Error closing HTTP client: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/admin/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

