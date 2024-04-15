from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import sys
sys.path.append(r"/home/aleksey/Документы/RecSystem")
from config import settings

engine = create_async_engine(settings.database_url,echo=True)
async_session_maker = async_sessionmaker(engine,expire_on_commit=False,autoflush=True)
async def get_async_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session