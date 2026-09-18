#!/bin/bash
###############################################################################
# Test Script: Send a Grafana FIRING alert to the middleware
#
# Usage:
#   # If port-forwarding:
#   ./test-grafana-firing.sh
#
#   # If custom URL:
#   WEBHOOK_URL=http://your-url ./test-grafana-firing.sh
###############################################################################

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:8000}"

echo "🔴 Sending Grafana FIRING alert to ${WEBHOOK_URL}/webhook/grafana ..."
echo ""

curl -s -X POST "${WEBHOOK_URL}/webhook/grafana" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "firing",
    "alerts": [
      {
        "status": "firing",
        "labels": {
          "alertname": "HighCPUUsage",
          "instance": "web-server-01",
          "severity": "critical",
          "team": "platform",
          "env": "production"
        },
        "annotations": {
          "summary": "CPU usage is above 90% on web-server-01",
          "description": "The CPU usage on web-server-01 has been above 90% for the last 5 minutes. Current value: 94.2%",
          "runbook_url": "https://runbooks.example.com/high-cpu",
          "dashboardURL": "https://grafana.example.com/d/abc123/cpu-dashboard"
        },
        "startsAt": "'"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"'",
        "endsAt": "0001-01-01T00:00:00Z",
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
      "summary": "CPU usage is above 90% on web-server-01"
    },
    "externalURL": "https://grafana.example.com",
    "title": "[FIRING:1] HighCPUUsage (critical)",
    "message": "CPU usage is above 90% on web-server-01"
  }' | python3 -m json.tool 2>/dev/null || echo "(raw response above)"

echo ""
echo "✅ Done! Check your Slack channel for the firing alert."
echo ""
echo "⏳ Wait a few seconds, then run: ./test-grafana-resolved.sh"
