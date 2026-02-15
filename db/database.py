import os
import asyncpg
from dotenv import load_dotenv
# from pathlib import Path

# Wczytaj .env
# env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv()

DB_USER = os.getenv("APP_DB_USER")
DB_PASSWORD = os.getenv("APP_DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# Connection string asyncpg
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Database:
    _pool: asyncpg.pool.Pool = None

    @classmethod
    async def get_pool(cls) -> asyncpg.pool.Pool:
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                min_size=1,
                max_size=10,
                command_timeout=60,
                )
        return cls._pool

    @classmethod
    async def execute(cls, query: str, *args):
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            return await connection.execute(query, *args)
        

    @classmethod
    async def fetch(cls, query: str, *args):
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            return await connection.fetch(query, *args)


    @classmethod
    async def fetchrow(cls, query: str, *args):
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            return await connection.fetchrow(query, *args)