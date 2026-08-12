from typing import List

from app.models.schemas import RecipeRecommendation
from app.services.recipe_service import recipe_service
from fastapi import APIRouter, Header, Query
from nutrigraph_common.exceptions.base import (
    InfrastructureException,
    ResourceNotFoundException,
)

router = APIRouter()

def _resolve_user_id(x_user_email: str | None, user_id_query: str | None) -> str:
    user_id = x_user_email or user_id_query
    if not user_id:
        raise InfrastructureException(message="Identificador de usuario (X-User-Email) requerido", details={})
    return user_id

@router.get("/recommendations", response_model=List[RecipeRecommendation])
async def get_recipe_recommendations(
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    user_id: str | None = Query(None)
):
    target_user_id = _resolve_user_id(x_user_email, user_id)
    try:
        recommendations = await recipe_service.get_recommendations(target_user_id)
        return recommendations
    except Exception as e:
        raise InfrastructureException(message="Error fetching recommendations", details={"cause": str(e)}) from e

@router.get("/search", response_model=List[RecipeRecommendation])
async def search_by_macros(
    max_calories: float = Query(...), 
    min_protein: float = Query(...),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    user_id: str | None = Query(None)
):
    target_user_id = _resolve_user_id(x_user_email, user_id)
    try:
        return await recipe_service.search_by_macros(target_user_id, max_calories, min_protein)
    except Exception as e:
        raise InfrastructureException(message="Error searching recipes", details={"cause": str(e)}) from e

@router.get("/search_advanced", response_model=List[RecipeRecommendation])
async def search_advanced(
    max_calories: float | None = Query(None),
    min_protein: float | None = Query(None),
    ingredient: str | None = Query(None),
    name: str | None = Query(None),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    user_id: str | None = Query(None)
):
    target_user_id = _resolve_user_id(x_user_email, user_id)
    try:
        return await recipe_service.search_advanced(target_user_id, max_calories, min_protein, ingredient, name)
    except Exception as e:
        raise InfrastructureException(message="Error searching advanced recipes", details={"cause": str(e)}) from e

@router.get("/verify")
async def verify_compatibility(
    ingredient_name: str = Query(...),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    user_id: str | None = Query(None)
):
    target_user_id = _resolve_user_id(x_user_email, user_id)
    try:
        is_compatible = await recipe_service.verify_compatibility(target_user_id, ingredient_name)
        return {"compatible": is_compatible}
    except Exception as e:
        raise InfrastructureException(message="Error verifying compatibility", details={"cause": str(e)}) from e

@router.get("/{recipe_id}/breakdown")
async def get_recipe_breakdown(recipe_id: str):
    try:
        breakdown = await recipe_service.get_recipe_breakdown(recipe_id)
        if not breakdown["recipe_name"]:
            raise ResourceNotFoundException(message="Recipe not found", details={"recipe_id": recipe_id})
        return breakdown
    except ResourceNotFoundException:
        raise
    except Exception as e:
        raise InfrastructureException(message="Error getting recipe breakdown", details={"cause": str(e)}) from e
