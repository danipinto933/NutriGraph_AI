from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from nutrigraph_common.exceptions.base import NutriGraphException

logger = logging.getLogger(__name__)

async def nutrigraph_exception_handler(request: Request, exc: NutriGraphException):
    logger.error(
        f"NutriGraphException interceptada: {exc.message} | "
        f"Status: {exc.status_code} | Detalles: {exc.details} | "
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )

def register_exception_handlers(app):
    """Registra los manejadores globales en la instancia de FastAPI."""
    app.add_exception_handler(NutriGraphException, nutrigraph_exception_handler)
