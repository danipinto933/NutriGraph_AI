from app.core.config import settings
from langchain_community.chat_message_histories import RedisChatMessageHistory


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """Obtiene el historial de chat de Redis para una sesión específica."""
    return RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        key_prefix="chat_history:",
        ttl=86400  # 24 hours
    )
