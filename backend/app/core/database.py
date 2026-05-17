import asyncpg

from app.core.config import settings


class Database:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(settings.database_url)

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def fetchval(self, query: str, *args):
        if self.pool is None:
            raise RuntimeError("Database pool is not initialized")

        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)


database = Database()