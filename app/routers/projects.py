from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from app.dependencies import dbSession, get_project_or_404, CurrentUser
from app.models import Project

from app.schemas import (ProjectCreate,
                     ProjectRead,
                     ProjectWithDetails)


router = APIRouter(prefix='/projects', tags=['Проекты'])



    
@router.post('/', response_model=ProjectRead) #Создание проекта
async def create_project(db: dbSession,
                      project: ProjectCreate,
                      current_user: CurrentUser):

    new_project = Project(
        title = project.title,
        description = project.description,
        owner_id = current_user.id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@router.get('/', response_model=list[ProjectRead])# Вывод всех проектов авторизованного пользователя
async def get_projects(db: dbSession,
                       current_user: CurrentUser):
    result = await db.execute(select(Project).where(Project.owner_id == current_user.id))
    return result.scalars().all()


@router.get('/{project_id}', response_model=ProjectWithDetails) # Вывод определенного проекта, доступен просмотр только своих проектов
async def get_project(project_id: int,
                      db: dbSession,
                      current_user: CurrentUser,):

    project = await get_project_or_404(project_id, db, current_user)
    return project

@router.delete('/{project_id}') #Удаление проекта авторизованного пользователя
async def delete_project(project_id: int,
                         db: dbSession,
                         project: Project = Depends(get_project_or_404)):

    await db.delete(project)
    await db.commit()
    return {'message': f'Проект с id: {project_id} удален успешно'}

@router.put('/{project_id}', response_model = ProjectRead) #Изменение проекта авторизованного пользователя
async def update_project(db: dbSession,
                         project_data: ProjectCreate,
                         project: Project = Depends(get_project_or_404)):
    
    project.title = project_data.title
    project.description = project_data.description
    
    await db.commit()
    await db.refresh(project)
    return project