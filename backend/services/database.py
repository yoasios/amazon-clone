from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DATABASE_URL

# Convert sqlite:// to sqlite+aiosqlite:// for async support
async_database_url = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(async_database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

