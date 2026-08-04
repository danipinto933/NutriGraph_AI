from fastapi import APIRouter, HTTPException
from typing import List

from app.models.user_repository import user_repository

router = APIRouter()

@router.get("/diets", response_model=List[str])
async def get_diets():
    try:
        diets = await user_repository.get_diet_types()
        return diets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/allergens", response_model=List[str])
async def get_allergens():
    try:
        allergens = await user_repository.get_allergens()
        return allergens
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
