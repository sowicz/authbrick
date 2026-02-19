import pytest
from httpx import ASGITransport, AsyncClient
from dotenv import load_dotenv
from db.database import Database



from main import app 


@pytest.fixture(autouse=True)
async def reset_db_pool():
    # before test
    yield
    # after test
    if Database._pool:
        await Database._pool.close()
        Database._pool = None


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac