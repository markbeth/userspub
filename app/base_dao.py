from app.database import async_session_maker
from app.logger import logger

from abc import ABC, abstractmethod
from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError


class AbsDAO(ABC):
    
    @abstractmethod
    async def add(self, **kwargs):
        pass
    
    @abstractmethod
    async def delete(self, **kwargs):
        pass

    @abstractmethod
    async def find_by_id(self, id: int):
        pass

    @abstractmethod
    async def find_one_or_none(self, **kwargs):
        pass

    @abstractmethod
    async def find_all(self, **kwargs):
        pass


class BaseDAO:
    model = None
    
    @classmethod
    async def add(cls, **data):
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot add data"
            logger.error(msg, extra=data, exc_info=True)
    
    
    @classmethod
    async def add_return_obj(cls, **data):
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**data).returning(cls.model)
                new_obj = await session.execute(query)
                await session.commit()
                return new_obj.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot add and return data"
            logger.error(msg, extra=data, exc_info=True)
            
    
    @classmethod
    async def update(cls, filter_by: dict, **update_data):
        try:
            async with async_session_maker() as session:
                query = (
                    update(cls.model)
                    .filter_by(**filter_by)
                    .values(**update_data)
                    .returning(cls.model)
                )
                result = await session.execute(query)
                await session.commit()
                return result.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot update data"
            logger.error(msg, extra=update_data, exc_info=True)
            
        
    @classmethod
    async def delete(cls, id: int):
        try:
            async with async_session_maker() as session:
                query = cls.model.__table__.delete().where(cls.model.id == id)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot delete by id"
            extra = {"id": id}
            logger.error(msg, extra=extra, exc_info=True)
    
    
    @classmethod
    async def find_by_id(cls, model_id: int):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter(cls.model.id == model_id)
                result = await session.execute(query)
                return result.scalars().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find by id"
            extra = {"model_id": model_id}
            logger.error(msg, extra=extra, exc_info=True)
    
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find one or none"
            logger.error(msg, extra=filter_by, exc_info=True)
    
    
    @classmethod
    async def find_obj(cls, **filter_by):
        try: 
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find obj"
            logger.error(msg, extra=filter_by, exc_info=True)
    
    
    @classmethod
    async def find_all(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e,  SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find all"
            logger.error(msg, extra=filter_by, exc_info=True)
    
    