"""
Redis-backed state store for alert correlation.

Tracks the mapping: alert fingerprint → AlertState (which includes
the Slack message timestamp needed to update/thread-reply on resolution).

Uses async redis (redis.asyncio) for non-blocking I/O inside FastAPI.
"""

import json
from typing import Optional
from datetime import datetime, timezone

import redis.asyncio as aioredis

from app.config import settings
from app.constants import REDIS_PREFIX_ALERT, REDIS_PREFIX_DEDUP
from app.models import AlertState
from app.logging_config import get_logger

logger = get_logger(__name__)

# ── Module-level connection pool (initialized on first use) ──
_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Return (and lazily create) the shared async Redis client."""
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    return _pool


async def close_redis() -> None:
    """Cleanly shut down the Redis pool (call on app shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


# ──────────────────────────────────────────────────────────────
#  Alert state operations
# ──────────────────────────────────────────────────────────────

def _alert_key(fingerprint: str) -> str:
    return f"{REDIS_PREFIX_ALERT}{fingerprint}"


def _dedup_key(fingerprint: str) -> str:
    return f"{REDIS_PREFIX_DEDUP}{fingerprint}"


async def get_alert_state(fingerprint: str) -> Optional[AlertState]:
    """Retrieve the current state for a given alert fingerprint."""
    r = await get_redis()
    raw = await r.get(_alert_key(fingerprint))
    if raw is None:
        return None
    try:
        data = json.loads(raw)
        return AlertState(**data)
    except (json.JSONDecodeError, Exception) as exc:
        logger.warning(
            f"Corrupt alert state in Redis for {fingerprint}: {exc}",
            extra={"fingerprint": fingerprint},
        )
        return None


async def save_alert_state(state: AlertState) -> None:
    """Persist an alert state with TTL."""
    r = await get_redis()
    key = _alert_key(state.fingerprint)
    payload = state.model_dump_json()
    await r.set(key, payload, ex=settings.redis_ttl_seconds)
    logger.debug(
        f"Saved alert state: {state.fingerprint}",
        extra={"fingerprint": state.fingerprint, "status": state.status},
    )


async def delete_alert_state(fingerprint: str) -> None:
    """Remove alert state (e.g. after resolved + TTL grace)."""
    r = await get_redis()
    await r.delete(_alert_key(fingerprint))


# ──────────────────────────────────────────────────────────────
#  Deduplication
# ──────────────────────────────────────────────────────────────

async def is_duplicate_firing(fingerprint: str) -> bool:
    """
    Check if a FIRING alert with this fingerprint was already processed
    within the dedup window.

    Returns True if duplicate (should be skipped), False if new.
    """
    r = await get_redis()
    key = _dedup_key(fingerprint)
    exists = await r.exists(key)
    return bool(exists)


async def mark_firing_seen(fingerprint: str) -> None:
    """
    Record that a FIRING alert was processed.
    The key expires after the dedup window.
    """
    r = await get_redis()
    key = _dedup_key(fingerprint)
    await r.set(key, "1", ex=settings.dedup_window_seconds)


async def clear_dedup(fingerprint: str) -> None:
    """Clear the dedup marker (e.g. when an alert resolves)."""
    r = await get_redis()
    await r.delete(_dedup_key(fingerprint))


# ──────────────────────────────────────────────────────────────
#  Health check
# ──────────────────────────────────────────────────────────────

async def redis_health() -> bool:
    """Return True if Redis is reachable."""
    try:
        r = await get_redis()
        return await r.ping()
    except Exception:
        return False
