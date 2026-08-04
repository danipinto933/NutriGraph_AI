from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

from app.api.deps import get_current_admin
from app.models.user_repository import user_repository
from app.schemas.user import AllergenCreate, AllergenUpdate

router = APIRouter()

class AllergenResponse(BaseModel):
    name: str

@router.get("/", response_model=List[AllergenResponse])
async def get_all_allergens(admin_email: str = Depends(get_current_admin)):
    """Get all allergens (Admin only)"""
    allergens = await user_repository.get_allergens()
    return [{"name": a} for a in allergens]

@router.post("/", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED)
async def create_allergen(
    allergen_in: AllergenCreate, admin_email: str = Depends(get_current_admin)
):
    """Create a new allergen (Admin only)"""
    # Check if exists
    allergens = await user_repository.get_allergens()
    if allergen_in.name in allergens:
        raise HTTPException(status_code=400, detail="Allergen already exists")
        
    success = await user_repository.create_allergen(allergen_in.name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create allergen")
        
    return {"name": allergen_in.name}

@router.put("/{name}", response_model=AllergenResponse)
async def update_allergen(
    name: str, allergen_in: AllergenUpdate, admin_email: str = Depends(get_current_admin)
):
    """Update an allergen (Admin only)"""
    allergens = await user_repository.get_allergens()
    if name not in allergens:
        raise HTTPException(status_code=404, detail="Allergen not found")
        
    success = await user_repository.update_allergen(old_name=name, new_name=allergen_in.name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update allergen")
        
    return {"name": allergen_in.name}

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergen(name: str, admin_email: str = Depends(get_current_admin)):
    """Delete an allergen (Admin only)"""
    allergens = await user_repository.get_allergens()
    if name not in allergens:
        raise HTTPException(status_code=404, detail="Allergen not found")
        
    success = await user_repository.delete_allergen(name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete allergen")
    
    return None
