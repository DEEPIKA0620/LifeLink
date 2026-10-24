import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger("lifelink.supabase")

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """
    Initializes and returns the Supabase client safely.
    Prefers SUPABASE_SERVICE_ROLE_KEY if set, otherwise falls back to SUPABASE_KEY.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning("Supabase URL or Key not configured.")
        return None

    try:
        key_to_use = settings.SUPABASE_SERVICE_ROLE_KEY if settings.SUPABASE_SERVICE_ROLE_KEY else settings.SUPABASE_KEY
        _supabase_client = create_client(settings.SUPABASE_URL, key_to_use)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def is_supabase_configured() -> bool:
    """Checks whether valid Supabase configuration is present."""
    return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
