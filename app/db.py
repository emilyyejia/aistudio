import os
from typing import Optional
import asyncpg

DATABASE_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # allow startup to raise a clearer error; keep var for tools that import this module
    DATABASE_URL = None

_pool: Optional[asyncpg.pool.Pool] = None

async def connect():
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise RuntimeError("NEON_DATABASE_URL or DATABASE_URL must be set in environment")
        _pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)

async def close():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

async def fetchrow(query: str, *args):
    assert _pool is not None, "DB pool not initialized"
    async with _pool.acquire() as con:
        return await con.fetchrow(query, *args)

async def fetch(query: str, *args):
    assert _pool is not None, "DB pool not initialized"
    async with _pool.acquire() as con:
        return await con.fetch(query, *args)

async def execute(query: str, *args):
    assert _pool is not None, "DB pool not initialized"
    async with _pool.acquire() as con:
        return await con.execute(query, *args)
