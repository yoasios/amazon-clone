import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def add_cancellation_fee_column():
    """Add cancellation_fee column to orders table"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        try:
            # Add the column if it doesn't exist
            await conn.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN IF NOT EXISTS cancellation_fee INTEGER DEFAULT 0
            """))
            print("Successfully added cancellation_fee column to orders table")
        except Exception as e:
            print(f"Error adding column: {e}")
            raise
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_cancellation_fee_column())
