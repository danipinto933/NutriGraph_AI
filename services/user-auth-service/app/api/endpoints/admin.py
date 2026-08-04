from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_admin
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.security import get_password_hash
from app.kafka.producer import producer
from app.models.user_repository import user_repository
from app.schemas.user import (
    AdminUserCreate,
    AdminUserUpdate,
    UserProfileResponse,
)

router = APIRouter()

@router.get("/", response_model=list[UserProfileResponse])
async def get_all_users(admin_email: str = Depends(get_current_admin)):
    """Get all users (Admin only)"""
    users = await user_repository.get_all_users()
    return users

@router.post("/", response_model=UserProfileResponse)
async def create_user(
    user_in: AdminUserCreate, admin_email: str = Depends(get_current_admin)
):
    """Create a new user (Admin only)"""
    existing_user = await user_repository.get_user_by_email(user_in.email)
    if existing_user:
        raise UserAlreadyExistsException(email=user_in.email)

    hashed_password = get_password_hash(user_in.password)
    await user_repository.create_user(
        email=user_in.email,
        hashed_password=hashed_password,
        first_name=user_in.first_name,
    )
    
    if user_in.role != "user":
        await user_repository.update_user_admin(user_in.email, {"role": user_in.role})

    await producer.send_event(
        topic="user-events",
        key=user_in.email,
        value={
            "event": "UserRegistered",
            "email": user_in.email,
            "first_name": user_in.first_name,
            "role": user_in.role,
        },
    )

    user_profile = await user_repository.get_user_profile(user_in.email)
    return user_profile

@router.put("/{email}", response_model=UserProfileResponse)
async def update_user(
    email: str, user_in: AdminUserUpdate, admin_email: str = Depends(get_current_admin)
):
    """Update user role or basic info (Admin only)"""
    existing_user = await user_repository.get_user_profile(email)
    if not existing_user:
        raise UserNotFoundException(email=email)

    update_data = user_in.model_dump(exclude_unset=True)
    if not update_data:
        return await user_repository.get_user_profile(email)
        
    biometric_keys = {"sex", "weight_kg", "height_cm", "age_years", "activity_factor"}
    if any(k in update_data for k in biometric_keys):
        from app.services.biometrics import get_biometric_profile
        merged = existing_user.copy()
        merged.update(update_data)
        
        if all(merged.get(k) is not None for k in biometric_keys):
            bio = get_biometric_profile(
                sex=merged["sex"],
                weight_kg=merged["weight_kg"],
                height_cm=merged["height_cm"],
                age_years=merged["age_years"],
                activity_factor=merged["activity_factor"]
            )
            update_data["bmi"] = bio.bmi
            update_data["bmr"] = bio.bmr
            update_data["tdee"] = bio.tdee

    updated_profile = await user_repository.update_user_admin(email, update_data)
    
    await producer.send_event(
        topic="user-events",
        key=email,
        value={
            "event": "UserAdminUpdated",
            "email": email,
            "updates": update_data,
        },
    )
    return updated_profile

@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(email: str, admin_email: str = Depends(get_current_admin)):
    """Delete a user (Admin only)"""
    existing_user = await user_repository.get_user_by_email(email)
    if not existing_user:
        raise UserNotFoundException(email=email)

    deleted = await user_repository.delete_user(email)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete user")

    await producer.send_event(
        topic="user-events",
        key=email,
        value={
            "event": "UserDeleted",
            "email": email,
        },
    )
    return None
