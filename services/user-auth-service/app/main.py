import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.core.config import settings
from app.core.exceptions import DomainException
from app.kafka.producer import producer
from app.models.user_repository import user_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up User & Auth Service")
    try:
        await user_repository.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j on startup: {e}")
    
    try:
        await producer.start()
    except Exception as e:
        logger.warning(f"Failed to start Kafka Producer on startup: {e}")
        
    yield
    # Shutdown
    logger.info("Shutting down User & Auth Service")
    try:
        await producer.stop()
    except Exception as e:
        logger.warning(f"Error stopping Kafka Producer: {e}")
    try:
        await user_repository.close()
    except Exception as e:
        logger.warning(f"Error closing Neo4j connection: {e}")

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

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "context": exc.context
        }
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

