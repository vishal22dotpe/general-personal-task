"""
Normalizer for Prometheus Alertmanager webhook payloads.

Alertmanager sends a POST with JSON body:
{
  "status": "firing" | "resolved",
  "alerts": [
    {
      "status": "firing",
      "labels": {"alertname": "HighCPU", "instance": "node1", "severity": "critical"},
      "annotations": {"summary": "CPU > 90%", "description": "..."},
      "startsAt": "2024-01-01T00:00:00Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "fingerprint": "abc123"
    }
  ],
  "groupLabels": {...},
  "commonLabels": {...},
  ...
}
"""

from typing import Any, Dict, List
from datetime import datetime, timezone

from app.models import NormalizedAlert
from app.constants import (
    SOURCE_ALERTMANAGER,
    STATUS_FIRING,
    STATUS_RESOLVED,
    SEVERITY_WARNING,
)
from app.normalizers.fingerprint import generate_fingerprint
from app.logging_config import get_logger

logger = get_logger(__name__)

# Alertmanager uses this sentinel for "not ended yet"
_ALERTMANAGER_ZERO_TIME = "0001-01-01T00:00:00Z"


def _parse_ts(raw: str) -> datetime | None:
    """Parse an Alertmanager ISO timestamp, returning None for the zero value."""
    if not raw or raw == _ALERTMANAGER_ZERO_TIME:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def normalize_alertmanager(payload: Dict[str, Any]) -> List[NormalizedAlert]:
    """
    Convert an Alertmanager webhook payload into a list of NormalizedAlerts.

    Alertmanager can batch multiple alerts in one request so we return a list.
    """
    alerts: List[NormalizedAlert] = []

    for raw_alert in payload.get("alerts", []):
        labels = raw_alert.get("labels", {})
        annotations = raw_alert.get("annotations", {})
        alert_name = labels.get("alertname", "UnknownAlert")
        status = raw_alert.get("status", STATUS_FIRING).lower()

        # Use Alertmanager's own fingerprint if available, otherwise generate one
        am_fingerprint = raw_alert.get("fingerprint")
        if am_fingerprint:
            fingerprint = f"am-{am_fingerprint}"
        else:
            fingerprint = generate_fingerprint(
                source=SOURCE_ALERTMANAGER,
                alert_name=alert_name,
                labels=labels,
            )

        severity = labels.get("severity", SEVERITY_WARNING).lower()
        summary = annotations.get("summary", "")
        description = annotations.get("description", "")

        starts_at = _parse_ts(raw_alert.get("startsAt", ""))
        ends_at = _parse_ts(raw_alert.get("endsAt", ""))

        # Channel override from label or annotation
        channel = (
            labels.get("slack_channel")
            or annotations.get("slack_channel")
            or None
        )

        normalized = NormalizedAlert(
            fingerprint=fingerprint,
            alert_name=alert_name,
            source=SOURCE_ALERTMANAGER,
            status=STATUS_RESOLVED if status == "resolved" else STATUS_FIRING,
            severity=severity,
            summary=summary,
            description=description,
            labels=labels,
            annotations=annotations,
            starts_at=starts_at,
            ends_at=ends_at,
            slack_channel=channel,
        )
        alerts.append(normalized)
        logger.info(
            "Normalized Alertmanager alert",
            extra={
                "fingerprint": fingerprint,
                "alert_name": alert_name,
                "status": normalized.status,
                "source": SOURCE_ALERTMANAGER,
            },
        )

    return alerts
