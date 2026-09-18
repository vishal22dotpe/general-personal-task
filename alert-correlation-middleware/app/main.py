"""
FastAPI application — entrypoint for the Alert Correlation Middleware.

Exposes:
  POST /webhook/alertmanager   — Prometheus Alertmanager
  POST /webhook/grafana        — Grafana Unified Alerting
  POST /webhook/cloudwatch     — AWS CloudWatch (via SNS)
  POST /webhook/opensearch     — OpenSearch Alerting
  POST /webhook/generic        — Auto-detect source
  GET  /health                 — Health check
  GET  /ready                  — Readiness check (includes Redis)
  GET  /metrics                — Basic metrics (Prometheus format)
"""

import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, PlainTextResponse

from app.config import settings
from app.logging_config import setup_logging, get_logger
from app.constants import (
    SOURCE_ALERTMANAGER,
    SOURCE_GRAFANA,
    SOURCE_CLOUDWATCH,
    SOURCE_OPENSEARCH,
    VALID_SOURCES,
)
from app.normalizers import (
    normalize_alertmanager,
    normalize_grafana,
    normalize_cloudwatch,
    normalize_opensearch,
)
from app.services.processor import process_alert
from app.services.redis_store import close_redis, redis_health

# ── Setup structured logging ─────────────────────────────────
setup_logging()
logger = get_logger(__name__)

# ── Simple in-memory metrics ─────────────────────────────────
_metrics = {
    "alerts_received_total": 0,
    "alerts_firing_total": 0,
    "alerts_resolved_total": 0,
    "alerts_deduplicated_total": 0,
    "alerts_errors_total": 0,
    "webhook_requests_total": 0,
    "webhook_latency_seconds_sum": 0.0,
    "webhook_latency_seconds_count": 0,
}

# ── Source → normalizer mapping ──────────────────────────────
_NORMALIZERS = {
    SOURCE_ALERTMANAGER: normalize_alertmanager,
    SOURCE_GRAFANA: normalize_grafana,
    SOURCE_CLOUDWATCH: normalize_cloudwatch,
    SOURCE_OPENSEARCH: normalize_opensearch,
}


# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Starting {settings.app_name} ({settings.environment})",
        extra={"source": "startup"},
    )
    yield
    logger.info("Shutting down — closing Redis pool")
    await close_redis()


# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="Alert Correlation Middleware",
    description="Correlates firing & resolved alerts and threads them in Slack.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Auth helper ──────────────────────────────────────────────
def _verify_auth(authorization: Optional[str]) -> None:
    """Verify the shared webhook secret if configured."""
    if not settings.webhook_secret:
        return  # No auth configured
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    expected = f"Bearer {settings.webhook_secret}"
    if authorization != expected:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")


# ── Auto-detect source ───────────────────────────────────────
def _detect_source(payload: Dict[str, Any]) -> str:
    """Guess the alert source from payload structure."""
    if "alerts" in payload and "groupLabels" in payload:
        return SOURCE_ALERTMANAGER
    if "alerts" in payload and "commonLabels" in payload:
        return SOURCE_GRAFANA
    if "AlarmName" in payload or (
        payload.get("Type") == "Notification" and "AlarmName" in str(payload.get("Message", ""))
    ):
        return SOURCE_CLOUDWATCH
    if "monitor_id" in payload or "monitor_name" in payload:
        return SOURCE_OPENSEARCH
    # Fallback: check for Grafana-style (has alerts array but no groupLabels)
    if "alerts" in payload:
        return SOURCE_GRAFANA
    raise HTTPException(
        status_code=400,
        detail="Cannot auto-detect alert source. Use a source-specific endpoint.",
    )


# ──────────────────────────────────────────────────────────────
#  Webhook endpoints
# ──────────────────────────────────────────────────────────────

async def _process_webhook(
    source: str,
    payload: Dict[str, Any],
    authorization: Optional[str] = None,
) -> JSONResponse:
    """Shared processing logic for all webhook endpoints."""
    start = time.monotonic()
    _metrics["webhook_requests_total"] += 1

    _verify_auth(authorization)

    normalizer = _NORMALIZERS.get(source)
    if not normalizer:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")

    try:
        normalized_alerts = normalizer(payload)
    except Exception as exc:
        _metrics["alerts_errors_total"] += 1
        logger.error(f"Normalization failed for {source}: {exc}", extra={"source": source})
        raise HTTPException(status_code=422, detail=f"Failed to normalize payload: {exc}")

    results = []
    for alert in normalized_alerts:
        _metrics["alerts_received_total"] += 1
        if alert.status == "firing":
            _metrics["alerts_firing_total"] += 1
        elif alert.status == "resolved":
            _metrics["alerts_resolved_total"] += 1

        try:
            result = await process_alert(alert)
            if result.get("status") == "deduplicated":
                _metrics["alerts_deduplicated_total"] += 1
            results.append(result)
        except Exception as exc:
            _metrics["alerts_errors_total"] += 1
            logger.error(
                f"Processing failed for {alert.alert_name}: {exc}",
                extra={"fingerprint": alert.fingerprint, "source": source},
            )
            results.append({"status": "error", "fingerprint": alert.fingerprint, "error": str(exc)})

    elapsed = time.monotonic() - start
    _metrics["webhook_latency_seconds_sum"] += elapsed
    _metrics["webhook_latency_seconds_count"] += 1

    return JSONResponse(
        content={
            "accepted": True,
            "source": source,
            "alerts_processed": len(results),
            "results": results,
            "latency_ms": round(elapsed * 1000, 2),
        }
    )


@app.post("/webhook/alertmanager")
async def webhook_alertmanager(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Receive alerts from Prometheus Alertmanager."""
    payload = await request.json()
    return await _process_webhook(SOURCE_ALERTMANAGER, payload, authorization)


@app.post("/webhook/grafana")
async def webhook_grafana(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Receive alerts from Grafana Unified Alerting."""
    payload = await request.json()
    return await _process_webhook(SOURCE_GRAFANA, payload, authorization)


@app.post("/webhook/cloudwatch")
async def webhook_cloudwatch(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Receive alerts from AWS CloudWatch (via SNS)."""
    payload = await request.json()
    return await _process_webhook(SOURCE_CLOUDWATCH, payload, authorization)


@app.post("/webhook/opensearch")
async def webhook_opensearch(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Receive alerts from OpenSearch Alerting."""
    payload = await request.json()
    return await _process_webhook(SOURCE_OPENSEARCH, payload, authorization)


@app.post("/webhook/generic")
async def webhook_generic(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Auto-detect the alert source and process."""
    payload = await request.json()
    source = _detect_source(payload)
    return await _process_webhook(source, payload, authorization)


# ──────────────────────────────────────────────────────────────
#  Health / Readiness / Metrics
# ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness probe — always returns OK if the process is running."""
    return {"status": "ok", "service": settings.app_name}


@app.get("/ready")
async def readiness():
    """Readiness probe — checks Redis connectivity."""
    redis_ok = await redis_health()
    if not redis_ok:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "redis": "unreachable"},
        )
    return {"status": "ready", "redis": "connected"}


@app.get("/metrics")
async def metrics():
    """Basic Prometheus-format metrics."""
    lines = []
    for name, value in _metrics.items():
        prom_name = f"acm_{name}"
        lines.append(f"# TYPE {prom_name} counter" if "total" in name else f"# TYPE {prom_name} gauge")
        lines.append(f"{prom_name} {value}")
    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain")
