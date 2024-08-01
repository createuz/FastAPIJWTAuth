from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional
from passlib.context import CryptContext
from tortoise.transactions import in_transaction

from settings.models import User
from .auth import create_access_token, create_refresh_token, authorize, get_current_user

auth_router = APIRouter(prefix="/api/v1", tags=["AUTH"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    password: str = Field(min_length=8, max_length=20)
    password2: Optional[str] = Field(None, min_length=8, max_length=20)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr = None
    password: constr(min_length=8) = None
    password2: constr(min_length=8) = None

    class Config:
        orm_mode = True


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    if not user_data.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please repeat the password")

    if user_data.password != user_data.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    hashed_password = pwd_context.hash(user_data.password)
    user_data_dict = user_data.dict()
    user_data_dict["password_hash"] = hashed_password

    user_data_dict.pop("password")
    user_data_dict.pop("password2")

    existing_user = await User.filter(email=user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await User.create(**user_data_dict)
    return {"message": "User created successfully", "data": user}


@auth_router.post("/login")
async def login(user_data: UserLogin):
    user = await User.filter(email=user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"email": user.email})
    refresh_token = create_refresh_token({"email": user.email})
    await User.filter(email=user.email).update(refresh_token=refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@auth_router.post("/refresh_token")
async def refresh_token(token_data: dict = Depends(authorize)):
    return token_data


@auth_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return current_user
