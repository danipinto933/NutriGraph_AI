from pydantic import BaseModel, Field, ConfigDict
from typing import List

class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1)
    calorias_100g: float = Field(default=0.0, ge=0)
    proteinas_100g: float = Field(default=0.0, ge=0)
    grasas_100g: float = Field(default=0.0, ge=0)
    carbohidratos_100g: float = Field(default=0.0, ge=0)
    origen: str = Field(default="vegetal")
    categoria: str = Field(default="varios")
    allergens: List[str] = Field(default_factory=list)

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    pass

class IngredientResponse(IngredientBase):
    model_config = ConfigDict(from_attributes=True)

