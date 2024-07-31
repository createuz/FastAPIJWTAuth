from fastapi.routing import APIRouter
from settengs.auth import pwd_context, create_access_jwt, create_refresh_jwt, authorize, verified_user
from .user import User, UserGet, UserPost, UserLogin
from fastapi import Depends, status, HTTPException

auth_router = APIRouter(prefix='/api/v1', tags=['AUTH'])


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(body: UserPost):
    body.password_hash = pwd_context.hash(body.password_hash)
    data = body.model_dump(by_alias=False, exclude_unset=True)
    existing = await User.filter(email=body.email).exists()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    user_obj = await User.create(**data)
    user = await UserGet.from_tortoise_orm(user_obj)
    user_id = user.model_dump()['id']
    return user_id


@auth_router.post('/login')
async def login(body: UserLogin):
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid login')
    user = await User.filter(email=body.email).first()
    if not user:
        raise error
    matches = pwd_context.verify(body.password, user.password_hash)
    if not matches:
        raise error
    data = {'email': user.email}
    access_token = create_access_jwt(data)
    refresh_token = create_refresh_jwt(data)
    await User.filter(email=body.email).update(**{'refresh_token': refresh_token})
    return {
        'message': 'login successful',
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'type': 'bearer'
    }


@auth_router.post('/refresh_token')
async def refresh(token_data: dict = Depends(authorize)):
    return token_data


@auth_router.get('/data')
async def protected_data(user: User = Depends(verified_user)):
    return {'status': 'authorized', 'email': user.email}
