from tortoise.models import Model
from tortoise.fields import CharField, DatetimeField, IntField, TextField
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, Field, ValidationError, validator
from typing import Optional


class User(Model):
    id = IntField(pk=True)
    email = CharField(max_length=100, unique=True, null=False)
    first_name = CharField(max_length=50, null=True)
    last_name = CharField(max_length=50, null=True)
    password_hash = CharField(max_length=128, null=False)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    refresh_token = TextField(null=True)
    is_active = IntField(default=1)

    class Meta:
        table = "users"
        ordering = ["-created_at"]


UserGet = pydantic_model_creator(User, name="User")


class UserPost(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    password: str = Field(min_length=8, max_length=20)
    password2: str = Field(min_length=8, max_length=20)

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValidationError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
