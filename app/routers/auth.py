from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.schemas import Token
from app.models import User
from app.dependencies import dbSession
from app.security import (verify_password, create_access_token, 
                          hash_password, create_refresh_token, 
                          decode_access_token)
from app.config import settings
from app.schemas import UserCreate, UserRead


router = APIRouter(prefix='/auth', tags=['Аутентификация'])


@router.post('/register', response_model=UserRead)
async def register(db: dbSession,
                   user: UserCreate,
                   response: Response):
    result = await db.execute(select(User).limit(1))
    users = result.scalars().all()
    role = 'admin' if len(users) == 0 else 'user'

    new_user = User(
        name = user.name,
        email = user.email,
        password_hash = hash_password(user.password),
        city = user.city,
        role = role
    )

    
    
    
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail='Пользователь с таким email уже существует')
    
    access_token = create_access_token(data={'sub': str(new_user.id)})
    refresh_token = create_refresh_token(data={'sub': str(new_user.id)})

    #access_token
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes*60,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )

    #refresh_token
    response.set_cookie(
        key = settings.refresh_cookie_name,
        value = refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )

    return new_user

@router.post('/login', response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: dbSession,
    response: Response
):
    result = await db.execute(
        select(User).where(User.email == form.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail='Incorrect email or password', 
                            headers={"WWW-Authenticate": "Bearer"})
    
    access_token = create_access_token(data={'sub': str(user.id)})
    refresh_token = create_refresh_token(data={'sub': str(user.id)})

    #access_token
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes*60,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )

    #refresh_token
    response.set_cookie(
        key = settings.refresh_cookie_name,
        value = refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )

    return Token(access_token=access_token, token_type='bearer')



@router.post('/refresh')
async def refresh(request: Request, db: dbSession, response: Response):
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if refresh_token is None:
        raise HTTPException(status_code=401, detail='Refresh токен не найден')
    
    payload = decode_access_token(refresh_token)
    if payload is None or payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Refresh токен не действителен')
    
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail='ID пользователя отстутствует')
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    
    new_access_token = create_access_token(data={'sub': str(user_id)})
    response.set_cookie(
        key = settings.access_cookie_name,
        value = new_access_token,
        max_age=settings.access_token_expire_minutes*60,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )
    
    return Token(access_token=new_access_token, token_type='bearer')


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(
        key=settings.access_cookie_name,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
        )
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
        )
    return {'detail': 'Вы успешно вышли'}


    
