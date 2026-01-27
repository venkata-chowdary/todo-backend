from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# NeonDB connection string
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_zFRe2oZ9PEaV@ep-hidden-lab-ahh0fd2l-pooler.c-3.us-east-1.aws.neon.tech/neondb"

# Async Engine with SSL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": True}
)

# Async Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Initialize tables
async def init_db():
    from models import Todo
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
