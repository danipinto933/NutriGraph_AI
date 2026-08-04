from fastapi import APIRouter
from app.services.recipe_service import recipe_service

router = APIRouter()

@router.get("/graph")
async def get_graph_analytics():
    """Obtiene estadísticas y agregaciones del grafo Neo4j (Ingredientes más usados, recetas, alérgenos)."""
    return await recipe_service.get_graph_analytics()
