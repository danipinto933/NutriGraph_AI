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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await chat_repository.connect()
    yield
    await chat_repository.close()
    await http_client.aclose()

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}
