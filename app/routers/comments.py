from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.dependencies import dbSession, get_task_or_404, get_comment_or_404, CurrentUser
from app.models import Comment

from app.schemas import (CommentCreate,
                     CommentRead,
                     CommentWithDetails)


router = APIRouter(prefix='/comments', tags=['Comments'])


@router.post('/', response_model=CommentRead) #Создание коммента, привязка к пользователю
async def add_comment(comment: CommentCreate,
                      db: dbSession,
                      current_user: CurrentUser):
    await get_task_or_404(comment.task_id, db, current_user)

    new_comment = Comment(
        text = comment.text,
        task_id = comment.task_id,
        user_id = current_user.id
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment)
    
    return new_comment


@router.get('/', response_model=list[CommentRead]) #Получение всех комментов авторизованного пользователя
async def get_comments(db: dbSession,
                       current_user: CurrentUser):
    result = await db.execute(select(Comment).where(Comment.user_id == current_user.id))
    return result.scalars().all()


@router.get('/{task_id}/comments', response_model=list[CommentRead])  #Получить все комменты определенного задания авторизованного пользователя
async def get_task_comment(task_id: int,
                           db: dbSession,
                           current_user: CurrentUser):
    await get_task_or_404(task_id, db, current_user)

    result = await db.execute(select(Comment).where(Comment.task_id == task_id,
                                                    Comment.user_id == current_user.id))
    return result.scalars().all()


@router.get('/{comment_id}', response_model=CommentWithDetails) #Получение комментария авторизованного пользователя
async def get_comment(comment_id: int, 
                      db: dbSession,
                      current_user: CurrentUser):
    
    comment = await get_comment_or_404(comment_id, db, current_user)
    return comment

@router.delete('/{comment_id}') #Удаление комментария авторизованного пользователя
async def delete_comment(comment_id: int,
                         db: dbSession,
                         comment: Comment = Depends(get_comment_or_404)):
    await db.delete(comment)
    await db.commit()
    return {'message': f'Comment with id: {comment_id} has been successfully deleted'}

@router.put('/{comment_id}', response_model=CommentRead)
async def update_comment(db: dbSession,
                         comment_data: CommentCreate,
                         current_user: CurrentUser,
                         comment: Comment = Depends(get_comment_or_404)):
    await get_task_or_404(comment_data.task_id, db, current_user)

    comment.text = comment_data.text
    comment.task_id = comment_data.task_id

    await db.commit()
    await db.refresh(comment)

    return comment