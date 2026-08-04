from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

from app.api.deps import get_current_admin
from app.models.user_repository import user_repository
from app.schemas.user import DietTypeCreate, DietTypeUpdate

router = APIRouter()

class DietTypeResponse(BaseModel):
    name: str

@router.get("/", response_model=List[DietTypeResponse])
async def get_all_diet_types(admin_email: str = Depends(get_current_admin)):
    """Get all diet types (Admin only)"""
    diets = await user_repository.get_diet_types()
    return [{"name": d} for d in diets]

@router.post("/", response_model=DietTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_diet_type(
    diet_in: DietTypeCreate, admin_email: str = Depends(get_current_admin)
):
    """Create a new diet type (Admin only)"""
    # Check if exists
    diets = await user_repository.get_diet_types()
    if diet_in.name in diets:
        raise HTTPException(status_code=400, detail="Diet type already exists")
        
    success = await user_repository.create_diet_type(diet_in.name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create diet type")
        
    return {"name": diet_in.name}

@router.put("/{name}", response_model=DietTypeResponse)
async def update_diet_type(
    name: str, diet_in: DietTypeUpdate, admin_email: str = Depends(get_current_admin)
):
    """Update a diet type (Admin only)"""
    diets = await user_repository.get_diet_types()
    if name not in diets:
        raise HTTPException(status_code=404, detail="Diet type not found")
        
    success = await user_repository.update_diet_type(old_name=name, new_name=diet_in.name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update diet type")
        
    return {"name": diet_in.name}

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet_type(name: str, admin_email: str = Depends(get_current_admin)):
    """Delete a diet type (Admin only)"""
    diets = await user_repository.get_diet_types()
    if name not in diets:
        raise HTTPException(status_code=404, detail="Diet type not found")
        
    success = await user_repository.delete_diet_type(name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete diet type")
    
    return None
