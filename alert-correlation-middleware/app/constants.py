"""
Shared constants used across the application.
"""

# ── Alert status values ──────────────────────────────────────
STATUS_FIRING = "firing"
STATUS_RESOLVED = "resolved"

# ── Alert source identifiers ────────────────────────────────
SOURCE_ALERTMANAGER = "alertmanager"
SOURCE_GRAFANA = "grafana"
SOURCE_CLOUDWATCH = "cloudwatch"
SOURCE_OPENSEARCH = "opensearch"

VALID_SOURCES = {
    SOURCE_ALERTMANAGER,
    SOURCE_GRAFANA,
    SOURCE_CLOUDWATCH,
    SOURCE_OPENSEARCH,
}

# ── Slack colours ────────────────────────────────────────────
COLOR_FIRING = "#E01E5A"      # red
COLOR_RESOLVED = "#2EB67D"    # green
COLOR_WARNING = "#ECB22E"     # amber
COLOR_UNKNOWN = "#808080"     # grey

# ── Severity mapping ────────────────────────────────────────
SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITY_EMOJI = {
    SEVERITY_CRITICAL: "🔴",
    SEVERITY_WARNING: "🟡",
    SEVERITY_INFO: "🔵",
}

# ── Redis key prefixes ──────────────────────────────────────
REDIS_PREFIX_ALERT = "acm:alert:"
REDIS_PREFIX_DEDUP = "acm:dedup:"
