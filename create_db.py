import asyncio
import asyncpg

async def create_database():
    conn = await asyncpg.connect(
        user='postgres',
        password='prathamesh7770',
        host='localhost'
    )
    try:
        await conn.execute('CREATE DATABASE amazon_clone')
        print('Database amazon_clone created successfully')
    except asyncpg.DuplicateDatabaseError:
        print('Database amazon_clone already exists')
    finally:
        await conn.close()

asyncio.run(create_database())
