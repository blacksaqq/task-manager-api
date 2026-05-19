from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.schemas import Token
from app.models import User
from app.dependencies import dbSession
from app.security import verify_password, create_access_token


router = APIRouter(prefix='/auth', tags=['Аутентификация'])


@router.post('/login', response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: dbSession
):
    result = await db.execute(
        select(User).where(User.email == form.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password', headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={'sub': str(user.id)})
    return Token(access_token=access_token, token_type='bearer')

    
