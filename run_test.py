import asyncio
import os
import asyncpg
from app import auth

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv('NEON_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print('NEON_DATABASE_URL not set')
        return
    print('Using DATABASE_URL=', DATABASE_URL)
    pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        # create table if not exists
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
              id SERIAL PRIMARY KEY,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        ''')
        ts = int(asyncio.get_event_loop().time())
        email = f'test+{ts}@example.com'
        pwd = 'secret'
        hashed = auth.hash_password(pwd)
        print('Inserting user', email)
        row = await conn.fetchrow('INSERT INTO users (email,password_hash) VALUES ($1,$2) RETURNING id,email,created_at', email, hashed)
        print('Inserted:', dict(row))
        # verify select
        row2 = await conn.fetchrow('SELECT id,email,password_hash FROM users WHERE email=$1', email)
        ok = auth.verify_password(pwd, row2['password_hash'])
        print('Password verify:', ok)
        token = auth.create_access_token({'sub': str(row2['id']), 'email': row2['email']})
        print('Token (first 60 chars):', token[:60])
    await pool.close()

if __name__ == '__main__':
    asyncio.run(main())
