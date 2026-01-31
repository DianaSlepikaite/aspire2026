"""
Database connection and management for Supabase.
"""

from typing import Optional
from supabase import create_client, Client

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import ConfigurationError, StorageError


_supabase_client: Optional[Client] = None


async def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.

    Returns:
        Supabase client instance

    Raises:
        ConfigurationError: If Supabase credentials are not configured
    """
    global _supabase_client

    if _supabase_client is None:
        settings = get_settings()

        if not settings.has_supabase_credentials():
            raise ConfigurationError(
                "Supabase credentials not configured. "
                "Please set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY environment variables."
            )

        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_PUBLISHABLE_KEY
            )
        except Exception as e:
            raise StorageError(
                f"Failed to connect to Supabase: {str(e)}",
                details={"error": str(e)}
            )

    return _supabase_client


async def initialize_database():
    """
    Initialize database connection on application startup.
    """
    try:
        await get_supabase_client()
    except Exception as e:
        # Log error but don't fail startup - allow graceful degradation
        print(f"Warning: Database initialization failed: {e}")


async def close_database():
    """
    Close database connection on application shutdown.
    """
    global _supabase_client
    # Supabase client doesn't need explicit closing
    _supabase_client = None
