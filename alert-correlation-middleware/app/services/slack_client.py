"""
Slack API client for posting, updating, and threading alert messages.

Uses the Slack Web API via httpx (async HTTP) to avoid pulling in the
heavy slack_sdk dependency. Needs only the `chat:write` scope on the bot token.
"""

import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

from app.config import settings
from app.models import NormalizedAlert, AlertState
from app.constants import (
    STATUS_FIRING,
    STATUS_RESOLVED,
    COLOR_FIRING,
    COLOR_RESOLVED,
    COLOR_WARNING,
    SEVERITY_EMOJI,
    SEVERITY_CRITICAL,
    SEVERITY_WARNING,
)
from app.logging_config import get_logger

logger = get_logger(__name__)

SLACK_POST_URL = "https://slack.com/api/chat.postMessage"
SLACK_UPDATE_URL = "https://slack.com/api/chat.update"

# ── Retry config ─────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]  # seconds


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.slack_bot_token}",
        "Content-Type": "application/json; charset=utf-8",
    }


# ──────────────────────────────────────────────────────────────
#  Message formatting
# ──────────────────────────────────────────────────────────────

def _build_firing_blocks(alert: NormalizedAlert) -> List[Dict[str, Any]]:
    """Build Slack Block Kit blocks for a FIRING alert."""
    emoji = SEVERITY_EMOJI.get(alert.severity, "🔴")
    color = COLOR_FIRING if alert.severity == SEVERITY_CRITICAL else COLOR_WARNING

    fields = []
    if alert.labels:
        # Show up to 8 important labels
        for k, v in list(alert.labels.items())[:8]:
            fields.append({"type": "mrkdwn", "text": f"*{k}:*\n`{v}`"})

    blocks: List[Dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} FIRING: {alert.alert_name}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Source:* `{alert.source}` | *Severity:* `{alert.severity}` | *Status:* 🔴 `FIRING`",
            },
        },
    ]

    if alert.summary:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary:* {alert.summary}"},
        })

    if alert.description:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Description:* {alert.description[:500]}"},
        })

    if fields:
        blocks.append({
            "type": "section",
            "fields": fields[:10],  # Slack max 10 fields
        })

    # Runbook / dashboard links
    links = []
    for key in ("runbook_url", "dashboardURL", "panelURL", "monitor_url", "alert_url"):
        url = alert.annotations.get(key)
        if url:
            label = key.replace("_", " ").replace("URL", " URL").title()
            links.append(f"<{url}|{label}>")
    if links:
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": " | ".join(links)}],
        })

    fired_at = alert.starts_at.strftime("%Y-%m-%d %H:%M:%S UTC") if alert.starts_at else "now"
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": f"🔖 `{alert.fingerprint}` | ⏱ Fired at {fired_at}"},
        ],
    })

    return blocks, color


def _build_resolved_blocks(
    alert: NormalizedAlert,
    state: Optional[AlertState] = None,
) -> List[Dict[str, Any]]:
    """Build Slack Block Kit blocks for a RESOLVED update."""
    duration = ""
    if state and state.first_fired_at:
        ends = alert.ends_at or datetime.now(timezone.utc)
        delta = ends - state.first_fired_at
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        duration = " ".join(parts)

    blocks: List[Dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"✅ RESOLVED: {alert.alert_name}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Source:* `{alert.source}` | *Severity:* `{alert.severity}` | *Status:* ✅ `RESOLVED`",
            },
        },
    ]

    if alert.summary:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary:* {alert.summary}"},
        })

    timing_parts = []
    if state and state.first_fired_at:
        timing_parts.append(f"*Fired at:* {state.first_fired_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    resolved_at = (alert.ends_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    timing_parts.append(f"*Resolved at:* {resolved_at}")
    if duration:
        timing_parts.append(f"*Duration:* {duration}")
    if state and state.firing_count > 1:
        timing_parts.append(f"*Total firings:* {state.firing_count}")

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": "\n".join(timing_parts)},
    })

    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": f"🔖 `{alert.fingerprint}` | ✅ Resolved"},
        ],
    })

    return blocks, COLOR_RESOLVED


def _build_thread_reply_blocks(
    alert: NormalizedAlert,
    state: Optional[AlertState] = None,
) -> List[Dict[str, Any]]:
    """Build a concise thread reply for resolution details."""
    duration = ""
    if state and state.first_fired_at:
        ends = alert.ends_at or datetime.now(timezone.utc)
        delta = ends - state.first_fired_at
        total_seconds = max(0, int(delta.total_seconds()))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        duration = " ".join(parts)

    resolved_at = (alert.ends_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = f"✅ *Alert Resolved*\n*Resolved at:* {resolved_at}"
    if duration:
        text += f"\n*Duration:* {duration}"
    if state and state.firing_count > 1:
        text += f"\n*Total firings during incident:* {state.firing_count}"

    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        }
    ]


# ──────────────────────────────────────────────────────────────
#  Slack API calls (with retry)
# ──────────────────────────────────────────────────────────────

async def _slack_api_call(
    url: str,
    payload: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Make a Slack API call with exponential backoff retry."""
    import asyncio

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, json=payload, headers=_headers())
                data = resp.json()

                if data.get("ok"):
                    return data

                error = data.get("error", "unknown")
                # Rate limited — respect Retry-After header
                if error == "ratelimited":
                    retry_after = int(resp.headers.get("Retry-After", RETRY_BACKOFF[attempt]))
                    logger.warning(f"Slack rate limited, retrying in {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                logger.error(f"Slack API error: {error}", extra={"payload_channel": payload.get("channel")})
                return None

        except httpx.TimeoutException:
            logger.warning(f"Slack API timeout (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_BACKOFF[attempt])
        except Exception as exc:
            logger.error(f"Slack API exception: {exc}")
            return None

    logger.error("Slack API call failed after all retries")
    return None


async def post_firing_alert(
    alert: NormalizedAlert,
) -> Optional[str]:
    """
    Post a new FIRING alert to Slack.

    Returns:
        The Slack message `ts` (timestamp) on success, None on failure.
    """
    channel = alert.slack_channel or settings.slack_default_channel
    blocks, color = _build_firing_blocks(alert)

    payload = {
        "channel": channel,
        "text": f"🔴 FIRING: {alert.alert_name} [{alert.source}]",
        "blocks": blocks,
        "attachments": [{"color": color, "blocks": []}],
        "unfurl_links": False,
        "unfurl_media": False,
    }

    result = await _slack_api_call(SLACK_POST_URL, payload)
    if result:
        ts = result.get("ts")
        logger.info(
            "Posted firing alert to Slack",
            extra={
                "fingerprint": alert.fingerprint,
                "alert_name": alert.alert_name,
                "slack_ts": ts,
                "source": alert.source,
            },
        )
        return ts
    return None


async def update_to_resolved(
    alert: NormalizedAlert,
    state: AlertState,
) -> bool:
    """
    Update the original FIRING message in-place to show RESOLVED status.

    Returns True on success.
    """
    channel = state.slack_channel
    blocks, color = _build_resolved_blocks(alert, state)

    payload = {
        "channel": channel,
        "ts": state.slack_message_ts,
        "text": f"✅ RESOLVED: {alert.alert_name} [{alert.source}]",
        "blocks": blocks,
        "attachments": [{"color": color, "blocks": []}],
    }

    result = await _slack_api_call(SLACK_UPDATE_URL, payload)
    if result:
        logger.info(
            "Updated Slack message to RESOLVED",
            extra={
                "fingerprint": alert.fingerprint,
                "alert_name": alert.alert_name,
                "slack_ts": state.slack_message_ts,
                "source": alert.source,
            },
        )
        return True
    return False


async def post_thread_reply(
    alert: NormalizedAlert,
    state: AlertState,
) -> bool:
    """
    Post a resolution summary as a thread reply on the original alert.

    Returns True on success.
    """
    channel = state.slack_channel
    blocks = _build_thread_reply_blocks(alert, state)

    payload = {
        "channel": channel,
        "thread_ts": state.slack_message_ts,
        "text": f"✅ Resolved: {alert.alert_name}",
        "blocks": blocks,
        "unfurl_links": False,
    }

    result = await _slack_api_call(SLACK_POST_URL, payload)
    if result:
        logger.info(
            "Posted resolution thread reply",
            extra={
                "fingerprint": alert.fingerprint,
                "alert_name": alert.alert_name,
                "slack_ts": state.slack_message_ts,
                "source": alert.source,
            },
        )
        return True
    return False
