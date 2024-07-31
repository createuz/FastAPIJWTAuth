from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from settengs.user import User
from settengs.config import Config
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/token')
error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')


def create_access_jwt(data: dict):
    data['exp'] = datetime.utcnow() + Config.JWT_ACCESS_EXP
    data['mode'] = 'access token'
    return jwt.encode(data, Config.SECRET, Config.ALGORITHM)


def create_refresh_jwt(data: dict):
    data['exp'] = datetime.utcnow() + Config.JWT_REFRESH_EXP
    data['mode'] = 'refresh token'
    return jwt.encode(data, Config.SECRET, Config.ALGORITHM)


async def authorize(token: str = Depends(oauth_scheme)):
    try:
        data = jwt.decode(token, Config.SECRET, Config.ALGORITHM)
        if 'email' not in data and 'mode' not in data:
            raise error
        user = await User.filter(email=data['email']).first()
        if not user or token != user.refresh_token:
            raise error
        data = {'email': user.email}
        refresh_token = create_refresh_jwt(data)
        await User.filter(email=user.email).update(**{'refresh_token': refresh_token})
        access_token = create_access_jwt(data)
        return {'access_token': access_token, 'refresh_token': refresh_token, 'type': 'bearer'}
    except JWTError:
        raise error


async def verified_user(token: str = Depends(oauth_scheme)):
    try:
        data = jwt.decode(token, Config.SECRET, Config.ALGORITHM)
        if 'email' not in data and 'mode' not in data:
            raise error
        user = await User.filter(email=data['email']).first()
        if not user:
            raise error
        return user
    except JWTError:
        raise error
