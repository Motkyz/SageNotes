from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base

from .config import settingPostgres

engine = create_async_engine(settingPostgres.db_url_asyncpg, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

async def get_session():
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

Base = declarative_base()

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)