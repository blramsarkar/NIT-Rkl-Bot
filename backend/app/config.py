"""
==============================================================================
File: backend/app/config.py
Role: Application Configuration & Environment Settings
Purpose: Centralizes configuration management using Pydantic BaseSettings.
         Configures LLM providers, database URL, CORS origins, abuse limits
         (rate limits, message length, daily LLM budget), admin auth, scraper
         allowlist, cache, and scheduled re-ingestion.
==============================================================================
"""

import logging
import os
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> project root is two levels above backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

DEFAULT_ORIGINS = "https://www.nitrkl.ac.in,https://nitrkl.ac.in"

logger = logging.getLogger("nitrkl_bot.config")


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "NIT Rourkela Chatbot API"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database: one SQLite file in <project>/data/ for the prototype, whichever
    # directory the server is started from. Use PostgreSQL in production.
    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'nitrkl_bot.db')}",
        description="postgresql://user:pass@host:5432/db in production; SQLite file for local testing."
    )

    # LLM providers
    PRIMARY_LLM_PROVIDER: str = Field(default="groq", description="'groq' or 'anthropic'")
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "openai/gpt-oss-20b"
    FALLBACK_LLM_MODEL: str = "openai/gpt-oss-120b"
    ANTHROPIC_MODEL: str = "claude-haiku-5-5"
    LLM_MAX_TOKENS: int = 800

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DIMENSION: int = 384

    # CORS: only the official site by default. "*" is refused in production.
    ALLOWED_ORIGINS: Union[str, List[str]] = DEFAULT_ORIGINS

    # Abuse & cost controls
    RATE_LIMIT_PER_MINUTE: int = 30
    MAX_QUESTIONS_PER_USER_WINDOW: int = 15
    USER_RATE_WINDOW_MINUTES: int = 10
    MAX_QUERY_CHARS: int = 500
    MAX_HISTORY_ITEMS: int = 6
    MAX_HISTORY_ITEM_CHARS: int = 2000
    DAILY_LLM_CALL_BUDGET: int = 2000  # LLM API calls per day (IST); 0 disables LLM use
    TRUST_PROXY_HEADERS: bool = False  # True only behind your own reverse proxy (nginx)

    # Admin: endpoints and admin UI are disabled unless a key is set
    ADMIN_API_KEY: str = ""

    # Scraper / ingestion
    NITRKL_BASE_URL: str = "https://www.nitrkl.ac.in"
    SCRAPE_ALLOWED_DOMAINS: str = "nitrkl.ac.in"  # comma-separated; subdomains allowed
    SCRAPE_MAX_BYTES: int = 2_000_000
    INGEST_DIR: str = os.path.join(DATA_DIR, "ingest")  # /admin/ingest only reads files here
    REINGEST_INTERVAL_HOURS: float = 12.0  # 0 disables scheduled re-ingestion
    REINGEST_INITIAL_DELAY_SECONDS: int = 60

    # Caching & verified answers
    CACHE_TTL_SECONDS: int = 900
    CACHE_MAX_ENTRIES: int = 500
    VERIFIED_MATCH_THRESHOLD: float = 0.82

    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_allowed_origins_list(self) -> List[str]:
        """Comma-separated ALLOWED_ORIGINS -> list. A wildcard is never allowed in production."""
        raw = self.ALLOWED_ORIGINS
        origins = [o.strip().rstrip("/") for o in (raw.split(",") if isinstance(raw, str) else raw) if o.strip()]
        if "*" in origins:
            if self.ENVIRONMENT.lower() == "production":
                logger.warning("ALLOWED_ORIGINS='*' is not allowed in production; using the nitrkl.ac.in origins.")
                return DEFAULT_ORIGINS.split(",")
            logger.warning("ALLOWED_ORIGINS='*' (development only). Do not deploy like this.")
        return origins

    def get_scrape_domains(self) -> List[str]:
        return [d.strip().lower().lstrip(".") for d in self.SCRAPE_ALLOWED_DOMAINS.split(",") if d.strip()]


settings = Settings()
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(settings.INGEST_DIR, exist_ok=True)
