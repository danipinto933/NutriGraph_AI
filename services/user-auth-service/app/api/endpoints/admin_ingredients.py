from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.deps import get_current_admin
from app.models.user_repository import user_repository
from app.schemas.ingredient import IngredientCreate, IngredientResponse, IngredientUpdate

router = APIRouter()

@router.get("/", response_model=List[IngredientResponse])
async def get_all_ingredients(admin_email: str = Depends(get_current_admin)):
    """Get all ingredients (Admin only)"""
    return await user_repository.get_ingredients()

@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    ingredient_in: IngredientCreate, admin_email: str = Depends(get_current_admin)
):
    """Create a new ingredient (Admin only)"""
    ingredients = await user_repository.get_ingredients()
    if any((i.get("name") or "").strip().lower() == ingredient_in.name.strip().lower() for i in ingredients):
        raise HTTPException(status_code=400, detail="El ingrediente ya existe")
        
    created = await user_repository.create_ingredient(ingredient_in.model_dump())
    if not created:
        raise HTTPException(status_code=500, detail="Error al crear ingrediente")
        
    return created

@router.put("/{name}", response_model=IngredientResponse)
async def update_ingredient(
    name: str, ingredient_in: IngredientUpdate, admin_email: str = Depends(get_current_admin)
):
    """Update an ingredient (Admin only)"""
    ingredients = await user_repository.get_ingredients()
    existing_names = [(i.get("name") or "") for i in ingredients]
    if name not in existing_names:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        
    updated = await user_repository.update_ingredient(old_name=name, data=ingredient_in.model_dump())
    if not updated:
        raise HTTPException(status_code=500, detail="Error al actualizar ingrediente")
        
    return updated

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(name: str, admin_email: str = Depends(get_current_admin)):
    """Delete an ingredient (Admin only)"""
    ingredients = await user_repository.get_ingredients()
    existing_names = [(i.get("name") or "") for i in ingredients]
    if name not in existing_names:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        
    success = await user_repository.delete_ingredient(name)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar ingrediente")
        
    return None
