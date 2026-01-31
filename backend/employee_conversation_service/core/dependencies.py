"""
FastAPI dependencies for dependency injection.
"""

from typing import AsyncGenerator
from functools import lru_cache

from employee_conversation_service.config import Settings, get_settings
from employee_conversation_service.core.database import get_supabase_client


@lru_cache
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


async def get_db_client():
    """
    Dependency for getting Supabase database client.

    Yields:
        Supabase client instance
    """
    client = await get_supabase_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass
