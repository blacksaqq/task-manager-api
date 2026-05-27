from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from app.dependencies import dbSession, get_project_or_404, get_user_or_404, get_task_or_404, CurrentUser
from app.models import Task
from sqlalchemy.orm import selectinload

from app.schemas import (TaskCreate,
                     TaskRead,
                     TaskWithDetails)


router = APIRouter(prefix='/tasks', tags=['Tasks'])


    
@router.post('/', response_model=TaskRead) #Создание задачи
async def add_task(task: TaskCreate,
                   db: dbSession,
                   current_user: CurrentUser):
    await get_project_or_404(task.project_id, db, current_user)

    
    new_task = Task(
        title = task.title,
        description = task.description,
        status = task.status,
        project_id = task.project_id,
        assignee_id = current_user.id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get('/', response_model=list[TaskRead]) #Получить все задачи авторизованного пользователя
async def get_tasks(db: dbSession,
                    current_user: CurrentUser):
    result = await db.execute(select(Task).where(Task.assignee_id == current_user.id))
    tasks = result.scalars().all()
    return tasks

@router.get('/{task_id}', response_model=TaskWithDetails) #Получить задачу, можно только свою
async def get_task(task_id: int,
                    db: dbSession,
                    current_user: CurrentUser):
    task = await get_task_or_404(task_id, db, current_user)
    return task

@router.delete('/{task_id}') #Удалить задачу, можно только свою
async def delete_task(db: dbSession,
                      task_id: int,
                      task: Task = Depends(get_task_or_404)):
    await db.delete(task)
    await db.commit()

    return {'message': f'Task with id: {task_id} has been successfully deleted'}
    

@router.put('/{task_id}', response_model=TaskRead) #Изменить задачу, только свою
async def update_task(db: dbSession,
                      task_data: TaskCreate,
                      current_user: CurrentUser,
                      task: Task = Depends(get_task_or_404)):
    await get_project_or_404(task_data.project_id, db, current_user)

    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.project_id = task_data.project_id


    await db.commit()
    await db.refresh(task)

    return task
