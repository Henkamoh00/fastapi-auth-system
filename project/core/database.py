from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from project.core import settings

# اختيار المحرك بناءً على نوع قاعدة البيانات
if "sqlite" in settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        pool_timeout=settings.POOL_TIMEOUT,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        pool_timeout=settings.POOL_TIMEOUT,
        pool_pre_ping=True,
    )

# إنشاء Session Async
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# إنشاء Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# دالة للحصول على جلسة قاعدة البيانات
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


# Base class الكلاس الأساسي لإنشاء النماذج
Base = declarative_base()


# إنشاء الجداول في قاعدة البيانات اذا لم تكن موجودة
async def create_tables():
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Connected to DB, table creation successful")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
