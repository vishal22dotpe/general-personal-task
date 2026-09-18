#!/bin/bash
###############################################################################
# Test Script: Check health and readiness of the middleware
###############################################################################

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:8000}"

echo "=== Health Check ==="
curl -s "${WEBHOOK_URL}/health" | python3 -m json.tool 2>/dev/null
echo ""

echo "=== Readiness Check ==="
curl -s "${WEBHOOK_URL}/ready" | python3 -m json.tool 2>/dev/null
echo ""

echo "=== Metrics ==="
curl -s "${WEBHOOK_URL}/metrics"
echo ""
