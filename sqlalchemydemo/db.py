'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 12:08:49
LastEditors: zhai
LastEditTime: 2024-05-25 21:16:16
'''

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Create asynchronous engine
DATABASE_URL = "sqlite+aiosqlite:///./sqlalchemy.db"
engine = create_async_engine(DATABASE_URL, echo=True, future=True,)

# Create asynchronous session maker
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Create base mapping class
# Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_session()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()


