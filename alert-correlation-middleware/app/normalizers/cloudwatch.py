"""
Normalizer for AWS CloudWatch Alarm payloads routed via SNS → webhook.

When a CloudWatch Alarm triggers an SNS topic that calls our webhook,
the payload looks like (after SNS JSON parsing):
{
  "AlarmName": "HighCPUUtilization",
  "AlarmDescription": "CPU utilization exceeds 90%",
  "AWSAccountId": "123456789012",
  "NewStateValue": "ALARM" | "OK" | "INSUFFICIENT_DATA",
  "NewStateReason": "Threshold Crossed: ...",
  "OldStateValue": "OK",
  "StateChangeTime": "2024-01-01T00:00:00.000+0000",
  "Region": "us-east-1",
  "AlarmArn": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighCPU",
  "Trigger": {
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Dimensions": [{"name": "InstanceId", "value": "i-12345"}],
    "Statistic": "Average",
    "Period": 300,
    "Threshold": 90.0,
    "ComparisonOperator": "GreaterThanThreshold",
    ...
  }
}

The raw SNS envelope wraps this in:
{
  "Type": "Notification",
  "Message": "<JSON string of the above>",
  ...
}
"""

import json
from typing import Any, Dict, List
from datetime import datetime

from app.models import NormalizedAlert
from app.constants import (
    SOURCE_CLOUDWATCH,
    STATUS_FIRING,
    STATUS_RESOLVED,
    SEVERITY_CRITICAL,
    SEVERITY_WARNING,
    SEVERITY_INFO,
)
from app.normalizers.fingerprint import generate_fingerprint
from app.logging_config import get_logger

logger = get_logger(__name__)

# CloudWatch state → our status mapping
_STATE_MAP = {
    "ALARM": STATUS_FIRING,
    "OK": STATUS_RESOLVED,
    "INSUFFICIENT_DATA": STATUS_FIRING,
}


def _unwrap_sns(payload: Dict[str, Any]) -> Dict[str, Any]:
    """If this is an SNS envelope, extract the inner Message."""
    if payload.get("Type") == "Notification" and "Message" in payload:
        try:
            return json.loads(payload["Message"])
        except (json.JSONDecodeError, TypeError):
            return payload
    return payload


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("+0000", "+00:00"))
    except (ValueError, TypeError):
        return None


def _build_labels(alarm: Dict[str, Any]) -> Dict[str, str]:
    """Build labels from CloudWatch dimensions and metadata."""
    labels: Dict[str, str] = {}

    trigger = alarm.get("Trigger", {})
    labels["namespace"] = trigger.get("Namespace", "")
    labels["metric_name"] = trigger.get("MetricName", "")
    labels["region"] = alarm.get("Region", "")
    labels["account_id"] = alarm.get("AWSAccountId", "")

    # Flatten dimensions
    for dim in trigger.get("Dimensions", []):
        name = dim.get("name", dim.get("Name", ""))
        value = dim.get("value", dim.get("Value", ""))
        if name and value:
            labels[f"dim_{name.lower()}"] = value

    return {k: v for k, v in labels.items() if v}


def _infer_severity(alarm: Dict[str, Any]) -> str:
    """Infer severity from the alarm state and trigger config."""
    state = alarm.get("NewStateValue", "").upper()
    if state == "INSUFFICIENT_DATA":
        return SEVERITY_INFO
    # Default to critical for ALARM, warning otherwise
    comparison = alarm.get("Trigger", {}).get("ComparisonOperator", "")
    if "GreaterThan" in comparison or "LessThan" in comparison:
        return SEVERITY_CRITICAL
    return SEVERITY_WARNING


def normalize_cloudwatch(payload: Dict[str, Any]) -> List[NormalizedAlert]:
    """
    Convert a CloudWatch Alarm (via SNS) payload into a list of NormalizedAlerts.
    Usually returns a single alert since CloudWatch sends one alarm per notification.
    """
    alarm = _unwrap_sns(payload)

    alert_name = alarm.get("AlarmName", "CloudWatchAlarm")
    state = alarm.get("NewStateValue", "ALARM").upper()
    status = _STATE_MAP.get(state, STATUS_FIRING)

    labels = _build_labels(alarm)
    fingerprint = generate_fingerprint(
        source=SOURCE_CLOUDWATCH,
        alert_name=alert_name,
        labels=labels,
    )

    severity = _infer_severity(alarm)
    summary = alarm.get("AlarmDescription", "")
    description = alarm.get("NewStateReason", "")

    annotations: Dict[str, str] = {}
    arn = alarm.get("AlarmArn", "")
    if arn:
        annotations["alarm_arn"] = arn
    old_state = alarm.get("OldStateValue", "")
    if old_state:
        annotations["old_state"] = old_state

    trigger = alarm.get("Trigger", {})
    if trigger:
        annotations["threshold"] = str(trigger.get("Threshold", ""))
        annotations["comparison"] = trigger.get("ComparisonOperator", "")
        annotations["statistic"] = trigger.get("Statistic", "")
        annotations["period"] = str(trigger.get("Period", ""))

    starts_at = _parse_ts(alarm.get("StateChangeTime", ""))
    ends_at = _parse_ts(alarm.get("StateChangeTime", "")) if status == STATUS_RESOLVED else None

    normalized = NormalizedAlert(
        fingerprint=fingerprint,
        alert_name=alert_name,
        source=SOURCE_CLOUDWATCH,
        status=status,
        severity=severity,
        summary=summary,
        description=description,
        labels=labels,
        annotations={k: v for k, v in annotations.items() if v},
        starts_at=starts_at,
        ends_at=ends_at,
    )

    logger.info(
        "Normalized CloudWatch alarm",
        extra={
            "fingerprint": fingerprint,
            "alert_name": alert_name,
            "status": status,
            "source": SOURCE_CLOUDWATCH,
        },
    )

    return [normalized]
