"""
BankSathi Backend Configuration

Reads all settings from environment variables.
Never hard-code secrets here.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Database
    database_url: str = (
        "postgresql+asyncpg://banksaathi:banksaathi@postgres:5432/banksaathi"
    )

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    jwt_secret: str = "insecure-dev-secret-replace-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # Providers
    llm_provider: Literal["mock", "gemini", "openai"] = "mock"
    voice_provider: Literal["mock", "google", "azure"] = "mock"
    bank_provider: Literal["mock"] = "mock"

    # API keys (optional — only needed for non-mock providers)
    llm_api_key: str = ""
    voice_api_key: str = ""

    # Risk engine thresholds
    risk_threshold_medium: int = 25
    risk_threshold_high: int = 50
    risk_threshold_critical: int = 75

    # Risk feature weights
    risk_weight_amount_deviation: int = 30
    risk_weight_new_beneficiary: int = 25
    risk_weight_unusual_time: int = 10
    risk_weight_untrusted_device: int = 30

    # Daily transaction limit (INR)
    daily_transaction_limit: int = 50000

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
