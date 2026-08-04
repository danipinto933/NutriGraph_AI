from fastapi import APIRouter
from app.models.chat_repository import chat_repository
from app.services.llm_agent import get_recent_latencies

router = APIRouter()

@router.get("/ai")
async def get_ai_analytics():
    """Obtiene métricas de uso y rendimiento del agente IA (latencias, conversaciones, ingredientes preguntados)."""
    latencies = get_recent_latencies()
    return await chat_repository.get_ai_analytics(latencies)
