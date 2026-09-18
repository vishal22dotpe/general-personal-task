"""
Normalizer for OpenSearch Alerting (Notification channel → webhook).

OpenSearch Alerting sends a POST when a monitor triggers:
{
  "monitor_id": "abc123",
  "monitor_name": "High Error Rate",
  "monitor_url": "https://opensearch.example.com/_plugins/_alerting/monitors/abc123",
  "trigger_id": "trigger1",
  "trigger_name": "error_rate_trigger",
  "trigger_severity": "1",
  "alert_id": "alert-uuid",
  "alert_name": "High Error Rate - error_rate_trigger",
  "state": "ACTIVE" | "COMPLETED" | "ERROR" | "ACKNOWLEDGED",
  "error_message": "",
  "alert_url": "https://...",
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-01-01T00:05:00Z",
  "results": [...]
}

Note: OpenSearch can also send Mustache-templated payloads; we handle
both the default and common custom formats.
"""

from typing import Any, Dict, List
from datetime import datetime

from app.models import NormalizedAlert
from app.constants import (
    SOURCE_OPENSEARCH,
    STATUS_FIRING,
    STATUS_RESOLVED,
    SEVERITY_CRITICAL,
    SEVERITY_WARNING,
    SEVERITY_INFO,
)
from app.normalizers.fingerprint import generate_fingerprint
from app.logging_config import get_logger

logger = get_logger(__name__)

# OpenSearch severity is 1-5 where 1 is highest
_SEVERITY_MAP = {
    "1": SEVERITY_CRITICAL,
    "2": SEVERITY_CRITICAL,
    "3": SEVERITY_WARNING,
    "4": SEVERITY_INFO,
    "5": SEVERITY_INFO,
}

# OpenSearch alert states
_STATE_MAP = {
    "ACTIVE": STATUS_FIRING,
    "COMPLETED": STATUS_RESOLVED,
    "ERROR": STATUS_FIRING,
    "ACKNOWLEDGED": STATUS_FIRING,
    "DELETED": STATUS_RESOLVED,
}


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def normalize_opensearch(payload: Dict[str, Any]) -> List[NormalizedAlert]:
    """
    Convert an OpenSearch Alerting webhook payload into NormalizedAlerts.
    """
    monitor_name = payload.get("monitor_name", "OpenSearchAlert")
    trigger_name = payload.get("trigger_name", "")
    alert_name = payload.get("alert_name", f"{monitor_name} - {trigger_name}".strip(" -"))

    state = payload.get("state", "ACTIVE").upper()
    status = _STATE_MAP.get(state, STATUS_FIRING)

    # Build identity labels
    labels: Dict[str, str] = {}
    monitor_id = payload.get("monitor_id", "")
    trigger_id = payload.get("trigger_id", "")
    if monitor_id:
        labels["monitor_id"] = monitor_id
    if trigger_id:
        labels["trigger_id"] = trigger_id

    fingerprint = generate_fingerprint(
        source=SOURCE_OPENSEARCH,
        alert_name=alert_name,
        labels=labels,
    )

    # Severity
    raw_severity = str(payload.get("trigger_severity", "3"))
    severity = _SEVERITY_MAP.get(raw_severity, SEVERITY_WARNING)

    # Annotations
    annotations: Dict[str, str] = {}
    alert_id = payload.get("alert_id", "")
    if alert_id:
        annotations["alert_id"] = alert_id
    monitor_url = payload.get("monitor_url", "")
    if monitor_url:
        annotations["monitor_url"] = monitor_url
    alert_url = payload.get("alert_url", "")
    if alert_url:
        annotations["alert_url"] = alert_url
    error_message = payload.get("error_message", "")
    if error_message:
        annotations["error_message"] = error_message

    # Summary / description
    summary = f"{alert_name} [{state}]"
    description = error_message or f"Monitor '{monitor_name}' trigger '{trigger_name}' is {state}"

    starts_at = _parse_ts(payload.get("period_start", ""))
    ends_at = _parse_ts(payload.get("period_end", ""))

    # If resolved, ends_at should reflect actual resolution
    if status == STATUS_RESOLVED and not ends_at:
        ends_at = _parse_ts(payload.get("period_end", ""))

    channel = payload.get("slack_channel", None)

    normalized = NormalizedAlert(
        fingerprint=fingerprint,
        alert_name=alert_name,
        source=SOURCE_OPENSEARCH,
        status=status,
        severity=severity,
        summary=summary,
        description=description,
        labels=labels,
        annotations=annotations,
        starts_at=starts_at,
        ends_at=ends_at,
        slack_channel=channel,
    )

    logger.info(
        "Normalized OpenSearch alert",
        extra={
            "fingerprint": fingerprint,
            "alert_name": alert_name,
            "status": status,
            "source": SOURCE_OPENSEARCH,
        },
    )

    return [normalized]
