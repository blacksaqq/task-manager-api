from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from dependencies import dbSession, get_project_or_404, get_user_or_404
from models import Project

from schemas import (ProjectCreate,
                     ProjectRead,
                     ProjectWithDetails)


router = APIRouter(prefix='/projects', tags=['Проекты'])



    
@router.post('/', response_model=ProjectRead)
async def create_project(db: dbSession,
                      project: ProjectCreate):
    await get_user_or_404(project.owner_id, db)

    new_project = Project(
        title = project.title,
        description = project.description,
        owner_id = project.owner_id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@router.get('/', response_model=list[ProjectRead])
async def get_projects(db: dbSession):
    result = await db.execute(select(Project))
    return result.scalars().all()


@router.get('/{project_id}', response_model=ProjectWithDetails)
async def get_project(project_id: int,
                      db: dbSession):
    query = (select(Project)
             .options(
                 selectinload(Project.owner),
                 selectinload(Project.tasks)
             ).where(Project.id == project_id))
    
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(status_code=404, detail='Проект не найден')
    else:
        return project

@router.delete('/{project_id}')
async def delete_project(project_id: int,
                         db: dbSession,
                         project: Project = Depends(get_project_or_404)):


    await db.delete(project)
    await db.commit()
    return {'message': f'Проект с id: {project_id} удален успешно'}

@router.put('/{project_id}', response_model = ProjectRead)
async def update_project(project_id: int,
                         db: dbSession,
                         project_data: ProjectCreate,
                         project: Project = Depends(get_project_or_404)):
    await get_user_or_404(project.owner_id, db)


    project.title = project_data.title
    project.description = project_data.description
    project.owner_id = project_data.owner_id
    
    await db.commit()
    await db.refresh(project)
    return project