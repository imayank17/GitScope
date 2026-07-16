from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger
from sqlalchemy.exc import SQLAlchemyError

logger = get_logger("app.database.session")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    logger.debug("Creating new database session")
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                logger.debug("Database session closed successfully")
            except SQLAlchemyError as e:
                logger.error(f"Database transaction failure, rolling back: {str(e)}")
                raise
    except Exception as e:
        logger.exception(f"Failed to establish database session: {str(e)}")
        raise