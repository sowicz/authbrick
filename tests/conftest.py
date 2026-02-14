import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from dotenv import load_dotenv


load_dotenv(".env.tests")  # Load test environment variables


from main import app 
from db.database import Database


@pytest_asyncio.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# @pytest.fixture(autouse=True)
# async def init_db_pool():
#     await Database.get_pool()

@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_db_pool():
    await Database.get_pool()

