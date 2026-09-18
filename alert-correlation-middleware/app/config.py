"""
Application configuration loaded from environment variables.
All secrets and tunables live here so they can be injected via
Kubernetes ConfigMaps / Secrets or docker-compose .env files.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Central configuration — every field maps to an env var."""

    # ── Slack ────────────────────────────────────────────────
    slack_bot_token: str = Field(
        ...,
        description="Slack Bot OAuth token (xoxb-…). Needs chat:write scope.",
    )
    slack_default_channel: str = Field(
        default="#alerts",
        description="Default Slack channel for alerts if not overridden per source.",
    )

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string.",
    )
    redis_ttl_seconds: int = Field(
        default=604800,  # 7 days
        description="TTL for alert state keys in Redis (seconds).",
    )

    # ── Alert behavior ───────────────────────────────────────
    dedup_window_seconds: int = Field(
        default=300,  # 5 minutes
        description="Window in which duplicate FIRING alerts are suppressed.",
    )
    resolve_update_original: bool = Field(
        default=True,
        description="Update the original Slack message in-place on resolve.",
    )
    resolve_thread_reply: bool = Field(
        default=True,
        description="Also post a thread reply with resolution details.",
    )

    # ── App ──────────────────────────────────────────────────
    app_name: str = "alert-correlation-middleware"
    app_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    environment: str = Field(default="production")

    # ── Webhook Auth (optional shared secret) ────────────────
    webhook_secret: Optional[str] = Field(
        default=None,
        description="Shared secret for validating incoming webhooks (Bearer token).",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton – import this everywhere
settings = Settings()
