from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from settings.config import Config
from settings.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_jwt(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)


def create_access_token(data: dict):
    return create_jwt(data, Config.JWT_ACCESS_EXP, "access")


def create_refresh_token(data: dict):
    return create_jwt(data, Config.JWT_REFRESH_EXP, "refresh")


async def authorize(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        if email is None or token_type != "access":
            raise credentials_exception
        user = await User.filter(email=email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


async def get_current_user(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        if email is None or token_type != "access":
            raise credentials_exception
        user = await User.filter(email=email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
