"""
FastAPI dependencies for dependency injection.
"""

from typing import AsyncGenerator
from functools import lru_cache

from client_need_service.config import Settings, get_settings
from client_need_service.core.database import get_db_pool


@lru_cache
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


async def get_db_client():
    """
    Dependency for getting PostgreSQL connection pool.

    Yields:
        asyncpg connection pool
    """
    pool = await get_db_pool()
    try:
        yield pool
    finally:
        # Cleanup if needed
        pass
