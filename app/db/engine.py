from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from app.config import settings

load_dotenv()

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_per_ping=True
)

sessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)



class Base(DeclarativeBase):
    pass

async def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        await db.close()

