"""
Consistent fingerprinting across all alert sources.

The fingerprint is a stable SHA-256 hash of the alert's identity fields
so that FIRING and RESOLVED events for the same incident always match.
"""

import hashlib
import json
from typing import Dict, Optional


def generate_fingerprint(
    source: str,
    alert_name: str,
    labels: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a deterministic fingerprint for an alert.

    The fingerprint is based on:
      - source (alertmanager, grafana, cloudwatch, opensearch)
      - alert_name (rule / alarm name)
      - sorted labels (key-value pairs that identify the alert instance)

    Returns:
        A 16-char hex digest (first 64 bits of SHA-256).
    """
    identity = {
        "source": source,
        "alert_name": alert_name,
        "labels": dict(sorted((labels or {}).items())),
    }
    raw = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
