from typing import Annotated
from pydantic import Field

SexField = Annotated[
    str, 
    Field(description="m or f (male or female)")
]

WeightField = Annotated[
    float, 
    Field(ge=30.0, le=300.0, description="Weight in kg (30 to 300)")
]

HeightField = Annotated[
    float, 
    Field(ge=100.0, le=250.0, description="Height in cm (100 to 250)")
]

AgeField = Annotated[
    int, 
    Field(ge=18, le=110, description="Age in years (18 to 110)")
]

ActivityFactorField = Annotated[
    float, 
    Field(ge=1.0, le=3.0, description="1.2 for sedentary, 1.55 for moderate, etc.")
]

DietTypeField = Annotated[
    str, 
    Field(description="Diet type: Vegana, Vegetariana, Carnivora, Mediterranea, etc.")
]

IntolerancesField = Annotated[
    list[str],
    Field(description="List of allergens/intolerances")
]
