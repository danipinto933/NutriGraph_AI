
from app.schemas.biometrics import BiometricProfile
from app.schemas.fields import (
    ActivityFactorField,
    AgeField,
    DietTypeField,
    HeightField,
    IntolerancesField,
    SexField,
    WeightField,
)
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    first_name: str
    role: str = "user"
    is_verified: bool = False

class UserRegisterResponse(BaseModel):
    message: str
    email: EmailStr
    is_verified: bool = False

class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserOnboarding(BaseModel):
    email: EmailStr
    first_name: str | None = None
    new_email: EmailStr | None = None
    sex: SexField
    weight_kg: WeightField
    height_cm: HeightField
    age_years: AgeField
    activity_factor: ActivityFactorField
    intolerances: IntolerancesField = Field(default_factory=list)
    diet_type: DietTypeField = "Mediterranea"

class OnboardingResponse(BaseModel):
    message: str
    biometrics: BiometricProfile

class UserProfileResponse(BaseModel):
    email: EmailStr
    first_name: str
    role: str = "user"
    sex: str | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    age_years: int | None = None
    activity_factor: float | None = None
    intolerances: list[str] = Field(default_factory=list)
    bmi: float | None = None
    bmr: float | None = None
    tdee: float | None = None
    diet_type: str | None = None

class AdminUserCreate(UserCreate):
    role: str = "user"

class AdminUserUpdate(BaseModel):
    first_name: str | None = None
    role: str | None = None
    sex: SexField | None = None
    weight_kg: WeightField | None = None
    height_cm: HeightField | None = None
    age_years: AgeField | None = None
    activity_factor: ActivityFactorField | None = None
    intolerances: IntolerancesField | None = None
    diet_type: DietTypeField | None = None

class DietTypeCreate(BaseModel):
    name: str

class DietTypeUpdate(BaseModel):
    name: str

class AllergenCreate(BaseModel):
    name: str

class AllergenUpdate(BaseModel):
    name: str
