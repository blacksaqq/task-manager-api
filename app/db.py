from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings


db_link = settings.database_url

engine = create_async_engine(
                            db_link,
                            echo = True
                            )

async_session = async_sessionmaker(
                                engine, 
                                expire_on_commit=False
                                )

class Base(DeclarativeBase):
    pass


