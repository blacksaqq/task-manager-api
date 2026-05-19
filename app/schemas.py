from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
    city: str = Field(min_length=1, max_length=255)

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    city: str

    model_config = {
        'from_attributes' : True
    }


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str

class ProjectRead(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    model_config = {
        'from_attributes' : True
    }


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(min_length=1, max_length=63)
    project_id: int = Field(gt=0)

class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    project_id: int

    model_config = {
        'from_attributes' : True
    }


    

class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=1023)
    task_id: int = Field(gt=0)

class CommentRead(BaseModel):
    id: int
    text: str
    task_id: int
    user_id: int

    model_config = {
        'from_attributes' : True
    }

#Модели с вложениями

class UserWithDetails(UserRead):
    tasks: list[TaskRead] = []
    projects: list[ProjectRead] = []

class ProjectWithDetails(ProjectRead):
    owner: Optional[UserRead] = None
    tasks: list[TaskRead] = []

class TaskWithDetails(TaskRead):
    assignee: Optional[UserRead] = None
    comment: list[CommentRead] = []

class CommentWithDetails(CommentRead):
    user: Optional[UserRead] = None
    task: Optional[TaskRead] = None



