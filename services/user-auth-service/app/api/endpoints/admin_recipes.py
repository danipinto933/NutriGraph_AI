from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.deps import get_current_admin
from app.models.user_repository import user_repository
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate

router = APIRouter()

@router.get("/", response_model=List[RecipeResponse])
async def get_all_recipes(admin_email: str = Depends(get_current_admin)):
    """Get all recipes (Admin only)"""
    recipes = await user_repository.get_recipes()
    return recipes

@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_in: RecipeCreate, admin_email: str = Depends(get_current_admin)
):
    """Create a new recipe (Admin only)"""
    recipes = await user_repository.get_recipes()
    if any((r.get("name") or "").strip().lower() == recipe_in.name.strip().lower() for r in recipes):
        raise HTTPException(status_code=400, detail="La receta ya existe")
        
    created = await user_repository.create_recipe(recipe_in.model_dump())
    if not created:
        raise HTTPException(status_code=500, detail="Error al crear la receta")
        
    return created

@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str, recipe_in: RecipeUpdate, admin_email: str = Depends(get_current_admin)
):
    """Update a recipe (Admin only)"""
    existing = await user_repository.get_recipe_by_id(recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
        
    updated = await user_repository.update_recipe(recipe_id=recipe_id, data=recipe_in.model_dump())
    if not updated:
        raise HTTPException(status_code=500, detail="Error al actualizar la receta")
        
    return updated

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: str, admin_email: str = Depends(get_current_admin)):
    """Delete a recipe (Admin only)"""
    existing = await user_repository.get_recipe_by_id(recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
        
    success = await user_repository.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar la receta")
        
    return None
