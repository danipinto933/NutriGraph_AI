from fastapi import APIRouter, status

from app.schemas.auth import Login, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import authenticate_user, register_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    return await register_user(user_in)

@router.post("/login", response_model=Token)
async def login(login_in: Login):
    return await authenticate_user(login_in)
