import os
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "LifeLink Emergency Blood & Medicine Locator System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./lifelink.db"

    # JWT Security
    JWT_SECRET_KEY: str = "lifelink_super_secret_jwt_key_2026_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # API Keys
    EMAIL_API_KEY: str = ""
    SMS_API_KEY: str = ""
    MAP_API_KEY: str = ""

    # Supabase Integration
    SUPABASE_URL: str = "https://loznqcvfnrodrpaifsfk.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvem5xY3ZmbnJvZHJwYWlmc2ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI4Mzk1ODIsImV4cCI6MjEwODQxNTU4Mn0.Cs0z86dcAEkRJz0ndm0cOPE8F-l-f4gVenZAFuQjY8g"
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_DB_URL: str = ""

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
