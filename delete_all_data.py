import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def delete_all_data():
    """Delete all data from PostgreSQL database"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        try:
            # Get all table names
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            # Drop all tables (cascade to handle dependencies)
            for table in tables:
                await conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
                print(f"Dropped table: {table}")
            
            print(f"Successfully deleted all data. Dropped {len(tables)} tables.")
            
        except Exception as e:
            print(f"Error deleting data: {e}")
            raise
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(delete_all_data())
