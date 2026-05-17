from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from typing import Optional


from db import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    city: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tasks: Mapped[list['Task']] = relationship(back_populates='assignee')
    projects: Mapped[list['Project']] = relationship(back_populates='owner')
    comments: Mapped[list['Comment']] = relationship(back_populates='user')

class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    owner: Mapped['User'] = relationship(back_populates='projects')
    tasks: Mapped[list['Task']] = relationship(back_populates='project')

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default='todo')
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    assignee_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    assignee : Mapped[Optional['User']] = relationship(back_populates='tasks')
    project: Mapped['Project'] = relationship(back_populates='tasks')
    comments: Mapped[list['Comment']] = relationship(back_populates = 'task')


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='comments')
    task: Mapped['Task'] = relationship(back_populates='comments')

