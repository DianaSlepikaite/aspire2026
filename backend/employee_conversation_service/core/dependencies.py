"""
FastAPI dependencies for dependency injection.
"""

from functools import lru_cache

from employee_conversation_service.config import Settings, get_settings
from employee_conversation_service.core.database import get_db_pool


@lru_cache
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


async def get_db_client():
    """
    Dependency for getting PostgreSQL database connection.

    Yields:
        asyncpg connection from pool
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        yield conn
