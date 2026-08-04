from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.exceptions import UserNotFoundException
from app.models.user_repository import user_repository
from app.schemas.user import (
    OnboardingResponse,
    UserOnboarding,
    UserProfileResponse,
)
from app.services.user_service import process_onboarding

router = APIRouter()


@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
    status_code=status.HTTP_200_OK,
    summary="User Onboarding (Biometrics)",
    description="Procesa el perfil biométrico del usuario, calcula IMC, TMB y GETD, y actualiza intolerancias alimentarias. Además emite eventos de actualización a través de Kafka al resto de microservicios.",
)
async def onboarding(
    onboarding_in: UserOnboarding, current_user_email: str = Depends(get_current_user)
):
    """
    Endpoint para completar el registro de un usuario y generar su perfil base de nutrición:

    - **email**: Correo del usuario (debe existir).
    - **sex**: Sexo biológico (m o f).
    - **weight_kg**: Peso en kg.
    - **height_cm**: Altura en centímetros.
    - **age_years**: Edad cronológica.
    - **activity_factor**: Factor de actividad física para el metabolismo (1.2 a 1.9).
    - **intolerances**: Lista opcional de intolerancias o alérgenos.
    """
    if onboarding_in.email.lower() != current_user_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this profile",
        )
    return await process_onboarding(onboarding_in)


@router.get("/me", response_model=UserProfileResponse)
async def read_users_me(current_user_email: str = Depends(get_current_user)):
    user = await user_repository.get_user_profile(current_user_email)
    if not user:
        raise UserNotFoundException(email=current_user_email)
    # Ensure intolerances is a list and ignore None from optional match
    intolerances = [i for i in user.get("intolerances", []) if i is not None]

    return UserProfileResponse(
        email=user["email"],
        first_name=user["first_name"],
        role=user.get("role", "user"),
        sex=user.get("sex"),
        weight_kg=user.get("weight_kg"),
        height_cm=user.get("height_cm"),
        age_years=user.get("age_years"),
        activity_factor=user.get("activity_factor"),
        bmi=user.get("bmi"),
        bmr=user.get("bmr"),
        tdee=user.get("tdee"),
        diet_type=user.get("diet_type"),
        intolerances=intolerances,
    )


@router.put("/profile", response_model=OnboardingResponse)
async def update_profile(
    profile_in: UserOnboarding, current_user_email: str = Depends(get_current_user)
):
    if profile_in.email.lower() != current_user_email.lower():
        raise HTTPException(
            status_code=403, detail="Not authorized to update this profile"
        )
    return await process_onboarding(profile_in)
