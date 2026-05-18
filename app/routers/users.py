from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.dependencies import dbSession, get_user_or_404
from app.models import User

from app.schemas import (UserCreate,
                     UserRead,
                     UserWithDetails)



router = APIRouter(prefix='/users', tags=['Пользователи'])



@router.post('/', response_model=UserRead)
async def create_user(db: dbSession,
                      user: UserCreate):
    
    new_user = User(
        name = user.name,
        email = user.email,
        city = user.city
    )

    
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail='Пользователь с таким email уже существует')


@router.get('/', response_model=list[UserRead])
async def get_users(db: dbSession):
    result = await db.execute(select(User))
    return result.scalars().all()
    
@router.get('/search', response_model=list[UserRead])
async def users_city(user_city: str,
                     db: dbSession):
    result = await db.execute(select(User).where(User.city.ilike(f'%{user_city}%')))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail=f'Пользователей из города "{user_city}" не было найдено')
    else:
        return users

@router.get('/{user_id}', response_model=UserWithDetails)
async def get_user(user_id: int,
                   db: dbSession,):
    query = (select(User).options(
        selectinload(User.tasks),
        selectinload(User.projects))
        .where(User.id == user_id))
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    else:
        return user

@router.delete('/{user_id}')
async def delete_user(user_id: int,
                      db: dbSession,
                      user: User = Depends(get_user_or_404)):
    await db.delete(user)
    await db.commit()
    return {'message': f'Пользователь с id: {user_id} удален'}


@router.put('/{user_id}', response_model=UserRead)
async def update_user(user_id: int,
                      db: dbSession,
                      user_data: UserCreate,
                      user: User = Depends(get_user_or_404)):
    user.name = user_data.name
    user.email = user_data.email
    user.city = user_data.city
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail='Пользователь с таким email уже существует')
    