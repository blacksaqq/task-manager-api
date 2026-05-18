from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import Annotated
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.tasks import router as tasks_router
from app.routers.comments import router as comments_router

from app.db import engine, Base, async_session




@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
