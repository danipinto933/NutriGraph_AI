from fastapi import APIRouter, Query, status

from app.schemas.auth import Login, Token
from app.schemas.user import ResendVerificationRequest, UserCreate, UserRegisterResponse
from app.services.user_service import (
    authenticate_user,
    register_user,
    resend_verification_email,
    verify_user_email,
)

router = APIRouter()

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    return await register_user(user_in)

@router.post("/login", response_model=Token)
async def login(login_in: Login):
    return await authenticate_user(login_in)

@router.get("/verify-email", response_model=Token)
async def verify_email(token: str = Query(..., description="Verification Magic Link Token")):
    return await verify_user_email(token)

@router.post("/resend-verification")
async def resend_verification(payload: ResendVerificationRequest):
    return await resend_verification_email(payload.email)

