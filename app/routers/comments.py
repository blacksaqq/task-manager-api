from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.dependencies import dbSession, get_user_or_404, get_task_or_404, get_comment_or_404
from app.models import Comment

from app.schemas import (CommentCreate,
                     CommentRead,
                     CommentWithDetails)


router = APIRouter(prefix='/comments', tags=['Комментарии'])


@router.post('/', response_model=CommentRead)
async def add_comment(comment: CommentCreate,
                      db: dbSession):
    await get_user_or_404(comment.user_id, db)
    await get_task_or_404(comment.task_id, db)

    new_comment = Comment(
        text = comment.text,
        task_id = comment.task_id,
        user_id = comment.user_id
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment)
    
    return new_comment


@router.get('/', response_model=list[CommentRead])
async def get_comments(db: dbSession):
    result = await db.execute(select(Comment))
    return result.scalars().all()


@router.get('/{task_id}/comments', response_model=list[CommentRead])
async def get_task_comment(task_id: int,
                           db: dbSession):
    await get_task_or_404(task_id, db)

    result = await db.execute(select(Comment).where(Comment.task_id == task_id))
    return result.scalars().all()


@router.get('/{comment_id}', response_model=CommentWithDetails)
async def get_comment(comment_id: int, db: dbSession):
    query = (
        select(Comment)
        .options(
            selectinload(Comment.user),
            selectinload(Comment.task)
        )
        .where(Comment.id == comment_id)
    )
    
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if comment is None:
        raise HTTPException(status_code=404, detail='Комментарий не найден')
    return comment

@router.delete('/{comment_id}')
async def delete_comment(comment_id: int,
                         db: dbSession,
                         comment: Comment = Depends(get_comment_or_404)):
    await db.delete(comment)
    await db.commit()
    return {'message': f'Комментарий c id: {comment_id} удален'}

