from pydantic import BaseModel


class BiometricProfile(BaseModel):
    bmi: float
    bmr: float
    tdee: float
