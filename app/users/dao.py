from app.base_dao import BaseDAO
from app.users.models import User
from app.database import async_session_maker

from sqlalchemy import update
from pydantic import EmailStr

class UserDAO(BaseDAO):
    model = User
    
    @classmethod
    async def update_verification_status(cls, email: str):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.email == email).values(is_verified=True)
            await session.execute(query)
            await session.commit()
    
    @classmethod
    async def downgrade_verification_status(cls, email: str):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.email == email).values(is_verified=False)
            await session.execute(query)
            await session.commit()