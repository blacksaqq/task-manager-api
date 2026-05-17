from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from dependencies import dbSession, get_project_or_404, get_user_or_404, get_task_or_404
from models import Task
from sqlalchemy.orm import selectinload

from schemas import (TaskCreate,
                     TaskRead,
                     TaskWithDetails)


router = APIRouter(prefix='/tasks', tags=['Задачи'])


    
@router.post('/', response_model=TaskRead)
async def add_task(task: TaskCreate,
                   db: dbSession):
    await get_project_or_404(task.project_id, db)

    if task.assignee_id is not None:
        await get_user_or_404(task.assignee_id, db)

    new_task = Task(
        title = task.title,
        description = task.description,
        status = task.status,
        project_id = task.project_id,
        assignee_id = task.assignee_id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get('/', response_model=list[TaskRead])
async def get_tasks(db: dbSession):
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

@router.get('/{task_id}', response_model=TaskWithDetails)
async def get_tasks(task_id: int,
                    db: dbSession):
    query = (select(Task)
    .options(
        selectinload(Task.assignee), 
        selectinload(Task.project))
        .where(Task.id == task_id))
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    else:
        return task

@router.delete('/{task_id}')
async def delete_task(db: dbSession,
                      task_id: int,
                      task: Task = Depends(get_task_or_404)):
    await db.delete(task)
    await db.commit()

    return {'message': f'Задача с id: {task_id} удалена успешно'}
    

@router.put('/{task_id}', response_model=TaskRead)
async def update_task(db: dbSession,
                      task_id: int,
                      task_data: TaskCreate,
                      task: Task = Depends(get_task_or_404)):
    await get_project_or_404(task_data.project_id, db)

    if task.assignee_id is not None:
        await get_user_or_404(task.assignee_id, db)

    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.project_id = task_data.project_id
    task.assignee_id = task_data.assignee_id

    await db.commit()
    await db.refresh(task)

    return task
