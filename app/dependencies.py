from fastapi import Depends, HTTPException, status, Request
from fastapi.security import  OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, Optional
from sqlalchemy.orm import selectinload, joinedload

from app.db import async_session
from app.models import User, Project, Task, Comment
from app.security import decode_access_token
from app.config import settings



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
    


    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login', auto_error=False)

async def get_current_user(
        request: Request,
        header_token: Annotated[Optional[str], Depends(oauth2_scheme)],
        db: dbSession
        ) -> User:
    token = header_token or request.cookies.get(settings.cookie_name)

    if token is None:
        raise HTTPException(status_code=401, detail='Токен не найден')

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, 
                            detail='Не удалось валидизировать учетные данные', 
                            headers={'WWW-Authenticate': 'Bearer'})
    user_id: int = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, 
                            detail='ID пользователя отсутствует в токене')
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_project_or_404(project_id: int,
                             db: dbSession,
                             current_user: CurrentUser):
    result = await db.execute(select(Project).where(Project.id == project_id,
                                                    Project.owner_id == current_user.id)
                                                    .options(joinedload(Project.owner),
                                                             selectinload(Project.tasks)))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail='Проект не найден или у вас нет доступа к нему')
    else:
        return project
    

async def get_task_or_404(task_id: int,
                          db: dbSession,
                          current_user: CurrentUser):
    result = await db.execute(select(Task).where(Task.id == task_id,
                                                 Task.assignee_id == current_user.id)
                                                 .options(joinedload(Task.assignee),
                                                          selectinload(Task.comments)))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail='Задача не найдена или у вас нет доступа к ней')
    else:
        return task

async def get_comment_or_404(comment_id: int,
                             db: dbSession,
                             current_user: CurrentUser):
    result = await db.execute(select(Comment).join(Comment.task)
                              .where(Comment.id == comment_id,
                                     Task.assignee_id == current_user.id)
                                     .options(joinedload(Comment.user),
                                              joinedload(Comment.task)))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail='Комментарий не найден или у вас нет доступа к нему')
    else:
        return comment
    

async def get_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Доступ запрещен!')
    return current_user

AdminUser = Annotated[User, Depends(get_admin_user)]

