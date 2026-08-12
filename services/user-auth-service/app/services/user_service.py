from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    EmailNotRegisteredException,
    UserNotVerifiedException,
    InvalidVerificationTokenException,
)
from app.core.security import (
    create_access_token,
    create_verification_token,
    get_password_hash,
    verify_email_token,
    verify_password,
)
from app.kafka.producer import producer
from app.models.user_repository import user_repository
from app.schemas.auth import Login, Token
from app.schemas.user import UserCreate, UserOnboarding, UserRegisterResponse, UserResponse
from app.services.biometrics import get_biometric_profile
from app.services.email_service import email_service


async def register_user(user_in: UserCreate) -> UserRegisterResponse:
    clean_email = user_in.email.strip().lower()
    existing_user = await user_repository.get_user_by_email(clean_email)
    if existing_user:
        raise UserAlreadyExistsException(email=clean_email)
        
    hashed_password = get_password_hash(user_in.password)
    await user_repository.create_user(
        email=clean_email, 
        hashed_password=hashed_password, 
        first_name=user_in.first_name.strip(),
        is_verified=False
    )
    
    verification_token = create_verification_token(clean_email)
    await email_service.send_verification_email(
        to_email=clean_email,
        first_name=user_in.first_name.strip(),
        verification_token=verification_token
    )
    
    return UserRegisterResponse(
        message="Usuario registrado correctamente. Por favor revisa tu correo electrónico para activar tu cuenta.",
        email=clean_email,
        is_verified=False
    )

async def verify_user_email(token: str) -> Token:
    email = verify_email_token(token)
    if not email:
        raise InvalidVerificationTokenException()
        
    user = await user_repository.get_user_by_email(email)
    if not user:
        raise UserNotFoundException(email=email)
        
    await user_repository.verify_user_email(email)
    
    await producer.send_event(
        topic="user-events",
        key=email,
        value={"event": "UserRegistered", "email": email, "first_name": user.get("first_name", ""), "role": user.get("role", "user")}
    )
    
    access_token = create_access_token(subject=user["email"], role=user.get("role", "user"))
    return Token(access_token=access_token, token_type="bearer")

async def resend_verification_email(email: str) -> dict[str, str]:
    clean_email = email.strip().lower()
    user = await user_repository.get_user_by_email(clean_email)
    if not user:
        raise EmailNotRegisteredException()
        
    if user.get("is_verified", False):
        return {"message": "La cuenta ya se encuentra verificada."}
        
    verification_token = create_verification_token(clean_email)
    await email_service.send_verification_email(
        to_email=clean_email,
        first_name=user.get("first_name", "Usuario"),
        verification_token=verification_token
    )
    return {"message": "Correo de verificación reenviado con éxito."}

async def authenticate_user(login_in: Login) -> Token:
    user = await user_repository.get_user_by_email(login_in.email)
    if not user:
        raise EmailNotRegisteredException()
        
    if not verify_password(login_in.password, user["hashed_password"]):
        raise InvalidCredentialsException()
        
    if not user.get("is_verified", False):
        raise UserNotVerifiedException(email=user["email"])
        
    access_token = create_access_token(subject=user["email"], role=user.get("role", "user"))
    return Token(access_token=access_token, token_type="bearer")


async def process_onboarding(onboarding_in: UserOnboarding):
    user = await user_repository.get_user_by_email(onboarding_in.email)
    if not user:
        raise UserNotFoundException(email=onboarding_in.email)
        
    bio_profile = get_biometric_profile(
        sex=onboarding_in.sex,
        weight_kg=onboarding_in.weight_kg,
        height_cm=onboarding_in.height_cm,
        age_years=onboarding_in.age_years,
        activity_factor=onboarding_in.activity_factor
    )
    
    biometrics_dict = {
        "sex": onboarding_in.sex,
        "weight_kg": onboarding_in.weight_kg,
        "height_cm": onboarding_in.height_cm,
        "age_years": onboarding_in.age_years,
        "activity_factor": onboarding_in.activity_factor,
        "bmi": bio_profile.bmi,
        "bmr": bio_profile.bmr,
        "tdee": bio_profile.tdee
    }
    
    if hasattr(onboarding_in, 'diet_type') and onboarding_in.diet_type:
        biometrics_dict["diet_type"] = onboarding_in.diet_type
    
    if onboarding_in.first_name:
        biometrics_dict["first_name"] = onboarding_in.first_name
    if onboarding_in.new_email:
        biometrics_dict["email"] = onboarding_in.new_email
    
    await user_repository.update_user_biometrics(
        email=onboarding_in.email,
        biometrics=biometrics_dict,
        intolerances=onboarding_in.intolerances
    )
    
    await producer.send_event(
        topic="user-events",
        key=onboarding_in.email,
        value={
            "event": "UserBiometricsUpdated", 
            "email": onboarding_in.email, 
            "biometrics": biometrics_dict
        }
    )
    
    if onboarding_in.intolerances:
        await producer.send_event(
            topic="user-events",
            key=onboarding_in.email,
            value={
                "event": "UserIntolerancesUpdated", 
                "email": onboarding_in.email, 
                "intolerances": onboarding_in.intolerances
            }
        )
        
    return {"message": "Onboarding processed successfully", "biometrics": bio_profile}
