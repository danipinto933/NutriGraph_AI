from fastapi import APIRouter, Depends
from app.api.deps import get_current_admin
from app.models.user_repository import user_repository

router = APIRouter()

@router.get("/users")
async def get_user_analytics(admin_email: str = Depends(get_current_admin)):
    """Obtiene analítica detallada de usuarios (Biometría, Sexo, Edad, Peso, Dietas, Intolerancias)."""
    analytics_data = await user_repository.get_user_analytics()
    return analytics_data
