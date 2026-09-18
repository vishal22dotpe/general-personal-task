"""
Core alert processing engine.

Orchestrates the full lifecycle:
1. Accept a NormalizedAlert
2. Check dedup (skip duplicate FIRINGs within the window)
3. On FIRING  → post to Slack, save state in Redis
4. On RESOLVED → update original message, thread reply, update state
"""

from datetime import datetime, timezone
from typing import Optional

from app.models import NormalizedAlert, AlertState
from app.config import settings
from app.constants import STATUS_FIRING, STATUS_RESOLVED
from app.services.redis_store import (
    get_alert_state,
    save_alert_state,
    is_duplicate_firing,
    mark_firing_seen,
    clear_dedup,
)
from app.services.slack_client import (
    post_firing_alert,
    update_to_resolved,
    post_thread_reply,
)
from app.logging_config import get_logger

logger = get_logger(__name__)


async def process_alert(alert: NormalizedAlert) -> dict:
    """
    Process a single normalized alert through the correlation pipeline.

    Returns a result dict with processing outcome.
    """
    fingerprint = alert.fingerprint

    if alert.status == STATUS_FIRING:
        return await _handle_firing(alert)
    elif alert.status == STATUS_RESOLVED:
        return await _handle_resolved(alert)
    else:
        logger.warning(f"Unknown alert status: {alert.status}", extra={"fingerprint": fingerprint})
        return {"status": "skipped", "reason": f"unknown status: {alert.status}"}


async def _handle_firing(alert: NormalizedAlert) -> dict:
    """Handle a FIRING alert."""
    fingerprint = alert.fingerprint

    # ── Check for duplicate within dedup window ──────────────
    if await is_duplicate_firing(fingerprint):
        # Still update the firing count if state exists
        existing = await get_alert_state(fingerprint)
        if existing:
            existing.firing_count += 1
            existing.last_fired_at = datetime.now(timezone.utc)
            await save_alert_state(existing)

        logger.info(
            f"Duplicate firing suppressed: {alert.alert_name}",
            extra={
                "fingerprint": fingerprint,
                "alert_name": alert.alert_name,
                "source": alert.source,
            },
        )
        return {
            "status": "deduplicated",
            "fingerprint": fingerprint,
            "message": "Duplicate firing suppressed within dedup window",
        }

    # ── Check if there's already an active alert ─────────────
    existing = await get_alert_state(fingerprint)
    if existing and existing.status == STATUS_FIRING:
        # Re-fire: increment count but don't post a new message
        existing.firing_count += 1
        existing.last_fired_at = datetime.now(timezone.utc)
        await save_alert_state(existing)
        await mark_firing_seen(fingerprint)

        logger.info(
            f"Re-fire detected (count={existing.firing_count}): {alert.alert_name}",
            extra={
                "fingerprint": fingerprint,
                "alert_name": alert.alert_name,
                "source": alert.source,
            },
        )
        return {
            "status": "re-fire",
            "fingerprint": fingerprint,
            "firing_count": existing.firing_count,
        }

    # ── New alert: post to Slack ─────────────────────────────
    slack_ts = await post_firing_alert(alert)
    if not slack_ts:
        logger.error(
            f"Failed to post alert to Slack: {alert.alert_name}",
            extra={"fingerprint": fingerprint, "source": alert.source},
        )
        return {"status": "error", "message": "Failed to post to Slack"}

    # ── Save state ───────────────────────────────────────────
    now = datetime.now(timezone.utc)
    channel = alert.slack_channel or settings.slack_default_channel
    state = AlertState(
        fingerprint=fingerprint,
        alert_name=alert.alert_name,
        source=alert.source,
        status=STATUS_FIRING,
        slack_channel=channel,
        slack_message_ts=slack_ts,
        firing_count=1,
        first_fired_at=alert.starts_at or now,
        last_fired_at=now,
    )
    await save_alert_state(state)
    await mark_firing_seen(fingerprint)

    logger.info(
        f"New alert processed: {alert.alert_name}",
        extra={
            "fingerprint": fingerprint,
            "alert_name": alert.alert_name,
            "source": alert.source,
            "slack_ts": slack_ts,
        },
    )

    return {
        "status": "posted",
        "fingerprint": fingerprint,
        "slack_ts": slack_ts,
        "channel": channel,
    }


async def _handle_resolved(alert: NormalizedAlert) -> dict:
    """Handle a RESOLVED alert."""
    fingerprint = alert.fingerprint

    # ── Look up the original alert state ─────────────────────
    state = await get_alert_state(fingerprint)
    if not state:
        logger.warning(
            f"Resolved alert with no matching state: {alert.alert_name}",
            extra={
                "fingerprint": fingerprint,
                "alert_name": alert.alert_name,
                "source": alert.source,
            },
        )
        # Post as a standalone resolved message (no original to update)
        slack_ts = await post_firing_alert(alert)
        return {
            "status": "resolved_orphan",
            "fingerprint": fingerprint,
            "message": "No matching firing alert found; posted standalone",
        }

    # ── Update the original message in-place ─────────────────
    updated = False
    if settings.resolve_update_original:
        updated = await update_to_resolved(alert, state)

    # ── Post a thread reply with resolution details ──────────
    threaded = False
    if settings.resolve_thread_reply:
        threaded = await post_thread_reply(alert, state)

    # ── Update state to resolved ─────────────────────────────
    now = datetime.now(timezone.utc)
    state.status = STATUS_RESOLVED
    state.resolved_at = alert.ends_at or now
    await save_alert_state(state)

    # ── Clear dedup marker so future firings are not suppressed
    await clear_dedup(fingerprint)

    logger.info(
        f"Alert resolved: {alert.alert_name}",
        extra={
            "fingerprint": fingerprint,
            "alert_name": alert.alert_name,
            "source": alert.source,
            "slack_ts": state.slack_message_ts,
        },
    )

    return {
        "status": "resolved",
        "fingerprint": fingerprint,
        "original_updated": updated,
        "thread_reply": threaded,
        "slack_ts": state.slack_message_ts,
    }
