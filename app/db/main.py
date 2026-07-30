from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
# 异步引擎
async_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
)

# 会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    # 开启数据库连接，并且启动事务
    async with async_engine.begin() as conn:
        # 同步创建数据表（ORM模型映射建表）
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
