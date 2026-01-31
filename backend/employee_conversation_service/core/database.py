"""
Database connection and management for PostgreSQL.
"""

import json
from typing import Optional
import asyncpg

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import ConfigurationError, StorageError


_db_pool: Optional[asyncpg.Pool] = None


async def _init_connection(conn):
    """Initialize connection with JSON codec for JSONB support."""
    await conn.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )


async def get_db_pool() -> asyncpg.Pool:
    """
    Get or create PostgreSQL connection pool.

    Returns:
        asyncpg connection pool

    Raises:
        ConfigurationError: If database credentials are not configured
        StorageError: If connection fails
    """
    global _db_pool

    if _db_pool is None:
        settings = get_settings()

        if not settings.has_database_credentials():
            raise ConfigurationError(
                "Database credentials not configured. "
                "Please set DATABASE_URL or individual DB settings in environment variables."
            )

        try:
            _db_pool = await asyncpg.create_pool(
                settings.get_database_url(),
                min_size=2,
                max_size=10,
                command_timeout=60,
                init=_init_connection
            )
        except Exception as e:
            raise StorageError(
                f"Failed to connect to PostgreSQL: {str(e)}",
                details={"error": str(e)}
            )

    return _db_pool


async def initialize_database():
    """
    Initialize database connection on application startup.
    """
    try:
        pool = await get_db_pool()
        # Test connection
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        print("Database connection established successfully")
    except Exception as e:
        # Log error but don't fail startup - allow graceful degradation
        print(f"Warning: Database initialization failed: {e}")


async def close_database():
    """
    Close database connection on application shutdown.
    """
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
