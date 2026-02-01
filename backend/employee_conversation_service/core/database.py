"""
Database connection and management for PostgreSQL.
"""

import json
from pathlib import Path
from typing import Optional
import asyncpg

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import ConfigurationError, StorageError

# Path to schema.sql relative to this file (core/database.py -> ../schema.sql)
SCHEMA_SQL_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


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


async def _ensure_schema(pool: asyncpg.Pool):
    """
    Check whether the employee_agent schema exists and create it
    (along with all tables, types, and indexes) from schema.sql if not.
    """
    async with pool.acquire() as conn:
        exists = await conn.fetchval(
            "SELECT EXISTS("
            "  SELECT 1 FROM information_schema.schemata"
            "  WHERE schema_name = 'employee_agent'"
            ")"
        )
        if exists:
            return

        if not SCHEMA_SQL_PATH.is_file():
            raise StorageError(
                f"Schema file not found at {SCHEMA_SQL_PATH}. "
                "Cannot initialise the employee_agent schema."
            )

        schema_sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
        await conn.execute(schema_sql)
        print(f"Database schema initialised from {SCHEMA_SQL_PATH}")


async def initialize_database():
    """
    Initialize database connection on application startup.
    Creates the employee_agent schema if it does not already exist.
    """
    try:
        pool = await get_db_pool()
        # Test connection
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        print("Database connection established successfully")

        # Ensure schema & tables exist
        await _ensure_schema(pool)
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
