from fastapi import Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordBearer
from jose import JWTError #будет удален, просто разбирался
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from db import async_session
from models import User, Project, Task, Comment
from security import decode_access_token
from models import User
from sqlalchemy import select
from config import settings



async def get_db():
    async with async_session() as session:
        yield session

dbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_user_or_404(user_id: int, db: dbSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    else:
        return user
    

async def get_project_or_404(project_id: int,
                             db: dbSession):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail='Проект не найден')
    else:
        return project
    
async def get_task_or_404(task_id: int,
                          db: dbSession):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    else:
        return task
    

async def get_comment_or_404(comment_id: int,
                             db: dbSession):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail='Комментарий не найден')
    else:
        return comment
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: dbSession
        ) -> User:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail='Не удалось валидизировать учетные данные', headers={'WWW-Authenticate': 'Bearer'})
    user_id: int = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail='ID пользователя отсутствует в токене')
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
