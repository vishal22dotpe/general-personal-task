"""
Normalizer for Grafana Alerting webhook payloads.

Grafana (unified alerting) sends a POST with JSON body:
{
  "status": "firing" | "resolved",
  "alerts": [
    {
      "status": "firing",
      "labels": {"alertname": "PanelAlert", "grafana_folder": "..."},
      "annotations": {"summary": "...", "description": "..."},
      "startsAt": "2024-01-01T00:00:00.000Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "fingerprint": "abc123",
      "silenceURL": "...",
      "dashboardURL": "...",
      "panelURL": "...",
      "valueString": "[ var='A' labels={} value=95.2 ]"
    }
  ],
  "groupLabels": {...},
  "commonLabels": {...},
  "commonAnnotations": {...},
  "externalURL": "https://grafana.example.com",
  "title": "[FIRING:1] ...",
  "message": "..."
}
"""

from typing import Any, Dict, List
from datetime import datetime, timezone

from app.models import NormalizedAlert
from app.constants import (
    SOURCE_GRAFANA,
    STATUS_FIRING,
    STATUS_RESOLVED,
    SEVERITY_WARNING,
)
from app.normalizers.fingerprint import generate_fingerprint
from app.logging_config import get_logger

logger = get_logger(__name__)

_GRAFANA_ZERO_TIME = "0001-01-01T00:00:00Z"


def _parse_ts(raw: str) -> datetime | None:
    if not raw or raw.startswith("0001"):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def normalize_grafana(payload: Dict[str, Any]) -> List[NormalizedAlert]:
    """
    Convert a Grafana unified-alerting webhook payload into NormalizedAlerts.
    """
    alerts: List[NormalizedAlert] = []

    for raw_alert in payload.get("alerts", []):
        labels = raw_alert.get("labels", {})
        annotations = raw_alert.get("annotations", {})
        alert_name = labels.get("alertname", payload.get("title", "GrafanaAlert"))
        status = raw_alert.get("status", STATUS_FIRING).lower()

        # Use Grafana's fingerprint if available
        gf_fingerprint = raw_alert.get("fingerprint")
        if gf_fingerprint:
            fingerprint = f"gf-{gf_fingerprint}"
        else:
            fingerprint = generate_fingerprint(
                source=SOURCE_GRAFANA,
                alert_name=alert_name,
                labels=labels,
            )

        severity = labels.get("severity", SEVERITY_WARNING).lower()
        summary = annotations.get("summary", payload.get("message", ""))
        description = annotations.get("description", "")

        # Enrich annotations with Grafana-specific URLs
        for url_key in ("silenceURL", "dashboardURL", "panelURL"):
            url_val = raw_alert.get(url_key)
            if url_val:
                annotations[url_key] = url_val
        value_string = raw_alert.get("valueString", "")
        if value_string:
            annotations["valueString"] = value_string

        starts_at = _parse_ts(raw_alert.get("startsAt", ""))
        ends_at = _parse_ts(raw_alert.get("endsAt", ""))

        channel = (
            labels.get("slack_channel")
            or annotations.get("slack_channel")
            or None
        )

        normalized = NormalizedAlert(
            fingerprint=fingerprint,
            alert_name=alert_name,
            source=SOURCE_GRAFANA,
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
            "Normalized Grafana alert",
            extra={
                "fingerprint": fingerprint,
                "alert_name": alert_name,
                "status": normalized.status,
                "source": SOURCE_GRAFANA,
            },
        )

    return alerts
