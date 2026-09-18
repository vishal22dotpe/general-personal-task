#!/bin/bash
###############################################################################
# Test Script: Send a Grafana RESOLVED alert to the middleware
#
# This should UPDATE the original firing message in-place and add
# a thread reply with resolution details.
#
# Usage:
#   # If port-forwarding:
#   ./test-grafana-resolved.sh
#
#   # If custom URL:
#   WEBHOOK_URL=http://your-url ./test-grafana-resolved.sh
###############################################################################

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:8000}"

echo "✅ Sending Grafana RESOLVED alert to ${WEBHOOK_URL}/webhook/grafana ..."
echo ""

curl -s -X POST "${WEBHOOK_URL}/webhook/grafana" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "alerts": [
      {
        "status": "resolved",
        "labels": {
          "alertname": "HighCPUUsage",
          "instance": "web-server-01",
          "severity": "critical",
          "team": "platform",
          "env": "production"
        },
        "annotations": {
          "summary": "CPU usage is back to normal on web-server-01",
          "description": "CPU usage dropped below threshold. Current value: 45.3%"
        },
        "startsAt": "'"$(date -u -d '-10 minutes' +%Y-%m-%dT%H:%M:%S.000Z 2>/dev/null || date -u -v-10M +%Y-%m-%dT%H:%M:%S.000Z)"'",
        "endsAt": "'"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"'",
        "fingerprint": "e4f5a6b7c8d9e0f1"
      }
    ],
    "groupLabels": {
      "alertname": "HighCPUUsage"
    },
    "commonLabels": {
      "alertname": "HighCPUUsage",
      "severity": "critical"
    },
    "commonAnnotations": {
      "summary": "CPU usage is back to normal on web-server-01"
    },
    "externalURL": "https://grafana.example.com",
    "title": "[RESOLVED] HighCPUUsage (critical)",
    "message": "CPU usage is back to normal on web-server-01"
  }' | python3 -m json.tool 2>/dev/null || echo "(raw response above)"

echo ""
echo "🎉 Done! Check your Slack channel:"
echo "   - The original FIRING message should now show ✅ RESOLVED"
echo "   - A thread reply should show the resolution duration"
