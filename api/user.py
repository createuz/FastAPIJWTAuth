from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from settengs.user import User

UserGet = pydantic_model_creator(User, name="User")


class UserPost(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    password_hash: str = Field(alias='password', min_length=8, max_length=20)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
