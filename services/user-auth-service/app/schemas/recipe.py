from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class RecipeIngredientItem(BaseModel):
    name: str = Field(..., min_length=1)
    grams: float = Field(..., gt=0)

class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(default="")

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientItem] = Field(default_factory=list)

class RecipeUpdate(RecipeBase):
    ingredients: List[RecipeIngredientItem] = Field(default_factory=list)

class RecipeResponse(RecipeBase):
    id: str
    ingredients: List[RecipeIngredientItem] = Field(default_factory=list)
    calories: float = Field(default=0.0)
    protein_g: float = Field(default=0.0)
    fat_g: float = Field(default=0.0)
    carbs_g: float = Field(default=0.0)

    model_config = ConfigDict(from_attributes=True)
