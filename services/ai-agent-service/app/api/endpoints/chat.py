import json
import logging

from app.services.llm_agent import stream_agent_response
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from nutrigraph_common.exceptions.base import ValidationException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

async def generate_chat_stream(user_id: str, session_id: str, message: str):
    try:
        async for chunk in stream_agent_response(user_id, session_id, message):
            # SSE format: data: <string>\n\n
            # We encode the chunk as JSON to safely escape newlines
            data = json.dumps({"content": chunk})
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Error in chat stream: {e}")
        # Note: the client expects SSE format, so we yield an error payload before disconnecting.
        error_data = json.dumps({"error": "Error processing chat"})
        yield f"data: {error_data}\n\n"

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise ValidationException(message="Message cannot be empty")
        
    return StreamingResponse(
        generate_chat_stream(request.user_id, request.session_id, request.message),
        media_type="text/event-stream"
    )

from app.models.chat_repository import chat_repository

@router.get("/conversations")
async def get_conversations(user_id: str):
    """Obtiene la lista de conversaciones anteriores de un usuario."""
    if not user_id:
        raise ValidationException(message="user_id is required")
    
    conversations = await chat_repository.get_user_conversations(user_id)
    return {"conversations": conversations}

@router.get("/conversations/{session_id}/messages")
async def get_conversation_history(session_id: str):
    """Obtiene el historial completo de mensajes de una sesión."""
    messages = await chat_repository.get_conversation_messages(session_id)
    return {"messages": messages}

