from typing import List, Optional

from pydantic import BaseModel, Field

# --- Anti-Corruption Layer: Kafka Events ---

class UserRegisteredEvent(BaseModel):
    """Esquema local para el evento UserRegistered"""
    email: str
    diet_type: Optional[str] = None
    # Otros campos no son relevantes para el grafo, los ignoramos.

class UserIntolerancesUpdatedEvent(BaseModel):
    """Esquema local para el evento UserIntolerancesUpdated"""
    user_id: str
    intolerances: List[str]

# --- API Response Schemas ---

class RecipeMacros(BaseModel):
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float

class RecipeRecommendation(BaseModel):
    recipe_id: str
    name: str
    description: str
    macros: RecipeMacros
    ingredients: List[str]
