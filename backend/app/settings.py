"""Runtime configuration, read once from the environment.

Everything that differs between a laptop and a deployment goes here, and nothing that
does not. Secrets are read from the environment or a local `.env` -- never committed,
never returned by an API, never logged (PLAN.md, Non-negotiable II).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LEKGOTLA_", env_file=".env", extra="ignore")

    # Relative to the backend/ directory, which is where alembic and uvicorn both run.
    database_url: str = "sqlite:///./lekgotla.db"


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is read once per process, not once per request."""
    return Settings()
