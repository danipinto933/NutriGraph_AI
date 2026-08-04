from typing import List

from app.models.schemas import RecipeRecommendation
from app.services.recipe_service import recipe_service
from fastapi import APIRouter, Query
from nutrigraph_common.exceptions.base import (
    InfrastructureException,
    ResourceNotFoundException,
)

router = APIRouter()

@router.get("/recommendations", response_model=List[RecipeRecommendation])
async def get_recipe_recommendations(user_id: str = Query(..., description="ID of the user to get recommendations for")):
    try:
        recommendations = await recipe_service.get_recommendations(user_id)
        return recommendations
    except Exception as e:
        raise InfrastructureException(message="Error fetching recommendations", details={"cause": str(e)}) from e

@router.get("/search", response_model=List[RecipeRecommendation])
async def search_by_macros(
    user_id: str = Query(...), 
    max_calories: float = Query(...), 
    min_protein: float = Query(...)
):
    try:
        return await recipe_service.search_by_macros(user_id, max_calories, min_protein)
    except Exception as e:
        raise InfrastructureException(message="Error searching recipes", details={"cause": str(e)}) from e

@router.get("/search_advanced", response_model=List[RecipeRecommendation])
async def search_advanced(
    user_id: str = Query(...),
    max_calories: float | None = Query(None),
    min_protein: float | None = Query(None),
    ingredient: str | None = Query(None),
    name: str | None = Query(None)
):
    try:
        return await recipe_service.search_advanced(user_id, max_calories, min_protein, ingredient, name)
    except Exception as e:
        raise InfrastructureException(message="Error searching advanced recipes", details={"cause": str(e)}) from e

@router.get("/verify")
async def verify_compatibility(
    user_id: str = Query(...),
    ingredient_name: str = Query(...)
):
    try:
        is_compatible = await recipe_service.verify_compatibility(user_id, ingredient_name)
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
