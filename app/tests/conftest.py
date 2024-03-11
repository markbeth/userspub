import asyncio
from sqlalchemy import insert
from app.database import Base, async_session_maker, async_engine
from app.config import settings
from app.users.models import User

import json
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    assert settings.MODE == "TEST"
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r") as f:
            return json.load(f)
    
    users = open_mock_json("users")
    # portfolios = open_mock_json("portfolios")
    
    async with async_session_maker() as session:
        add_users = insert(User).values(users)
        # add_portfolios = insert(Portfolio).values(portfolios)
        await session.execute(add_users)
        await session.commit()


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """
    Create an instance of the default event loop for each test case
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()