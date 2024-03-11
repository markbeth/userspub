from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}
    
async_engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
# engine = create_engine(DATABASE_URL)

async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
# session_maker = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """ 
    используется для миграции
    """
    pass 

