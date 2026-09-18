"""
Pydantic models for the normalized alert representation.
Every alert source is normalized into NormalizedAlert before processing.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class NormalizedAlert(BaseModel):
    """Unified alert representation regardless of source."""

    # ── Identity ─────────────────────────────────────────────
    fingerprint: str = Field(
        ...,
        description="Unique hash identifying this alert instance.",
    )
    alert_name: str = Field(
        ...,
        description="Human-readable alert name / rule name.",
    )
    source: str = Field(
        ...,
        description="Origin system: alertmanager | grafana | cloudwatch | opensearch.",
    )

    # ── Status ───────────────────────────────────────────────
    status: str = Field(
        ...,
        description="'firing' or 'resolved'.",
    )
    severity: str = Field(
        default="warning",
        description="Severity level: critical | warning | info.",
    )

    # ── Details ──────────────────────────────────────────────
    summary: str = Field(
        default="",
        description="One-line summary of the alert.",
    )
    description: str = Field(
        default="",
        description="Longer description or runbook link.",
    )
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="Key-value labels / dimensions.",
    )
    annotations: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional annotations (runbook_url, dashboard, etc.).",
    )

    # ── Timestamps ───────────────────────────────────────────
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None

    # ── Routing ──────────────────────────────────────────────
    slack_channel: Optional[str] = Field(
        default=None,
        description="Override the default Slack channel for this alert.",
    )


class AlertState(BaseModel):
    """State stored in Redis for an active alert."""

    fingerprint: str
    alert_name: str
    source: str
    status: str
    slack_channel: str
    slack_message_ts: str
    slack_thread_ts: Optional[str] = None
    firing_count: int = 1
    first_fired_at: datetime
    last_fired_at: datetime
    resolved_at: Optional[datetime] = None
