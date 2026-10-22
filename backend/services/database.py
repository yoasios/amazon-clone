from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DATABASE_URL

# Check if using SQLite or PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    # SQLite with aiosqlite driver
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False
    )
else:
    # PostgreSQL - add connection pooling
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20
    )
    

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

