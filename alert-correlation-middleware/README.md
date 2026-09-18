# 🔔 Alert Correlation Middleware

**Reduce Slack alert fatigue by ~50%** — correlates firing and resolved alerts into a single threaded Slack message instead of flooding your channel with separate notifications.

```
┌─────────────────┐
│  Alertmanager    │───┐
├─────────────────┤   │
│  Grafana         │───┤    ┌──────────────────────┐     ┌─────────┐
├─────────────────┤   ├───▶│  Alert Correlation    │────▶│  Slack  │
│  CloudWatch      │───┤    │  Middleware           │     │  API    │
├─────────────────┤   │    └──────────────────────┘     └─────────┘
│  OpenSearch      │───┘           │
└─────────────────┘          ┌─────┴──────┐
                             │   Redis    │
                             │  (state)   │
                             └────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **In-place resolution** | Updates the original 🔴 FIRING message to ✅ RESOLVED |
| **Thread replies** | Posts resolution details as a thread reply for audit trail |
| **Duplicate suppression** | Flapping alerts are deduplicated within a configurable window |
| **Multi-source** | Normalizes Alertmanager, Grafana, CloudWatch, and OpenSearch |
| **Auto-detect** | `/webhook/generic` endpoint auto-detects the alert source |
| **Rich formatting** | Slack Block Kit messages with severity, labels, runbook links |
| **Prometheus metrics** | `/metrics` endpoint for self-monitoring |
| **Kubernetes-native** | Helm chart + Kustomize overlays + HPA + PDB + NetworkPolicy |
| **Secure** | Non-root container, read-only filesystem, webhook auth, TLS |

## 📸 How It Works

### Before (2 messages per incident = noise)
```
#alerts channel:
  🔴 FIRING: HighCPU on node-1         ← message 1
  🔴 FIRING: DiskFull on node-3        ← message 2
  ✅ RESOLVED: HighCPU on node-1       ← message 3 (hard to correlate!)
  🔴 FIRING: HighMemory on node-2      ← message 4
  ✅ RESOLVED: DiskFull on node-3      ← message 5
```

### After (1 message per incident = clarity)
```
#alerts channel:
  ✅ RESOLVED: HighCPU on node-1       ← original message UPDATED in-place
     └─ 🧵 "Resolved after 12m 34s"   ← thread reply with duration
  🔴 FIRING: HighMemory on node-2      ← still active
  ✅ RESOLVED: DiskFull on node-3      ← original message UPDATED in-place
     └─ 🧵 "Resolved after 5m 12s"
```

---

## 🚀 Quick Start

### Prerequisites

- **Slack Bot Token** (`xoxb-...`) with `chat:write` scope
- **Docker** and **Docker Compose** (for local dev)
- **Kubernetes** cluster (for production deployment)

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App**
2. Under **OAuth & Permissions**, add the `chat:write` bot scope
3. Install to your workspace and copy the **Bot User OAuth Token** (`xoxb-...`)
4. Invite the bot to your alerts channel: `/invite @YourBotName`

### 2. Local Development (Docker Compose)

```bash
# Clone and configure
cd alert-correlation-middleware
cp .env.example .env
# Edit .env and set your SLACK_BOT_TOKEN

# Start the stack
docker compose up -d

# Verify
curl http://localhost:8000/health
# → {"status":"ok","service":"alert-correlation-middleware"}

curl http://localhost:8000/ready
# → {"status":"ready","redis":"connected"}
```

### 3. Test with a Sample Alert

```bash
# Send a FIRING alert (Alertmanager format)
curl -X POST http://localhost:8000/webhook/alertmanager \
  -H "Content-Type: application/json" \
  -d '{
    "status": "firing",
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "HighCPUUsage",
        "instance": "node-1",
        "severity": "critical"
      },
      "annotations": {
        "summary": "CPU usage is above 90% on node-1",
        "description": "The CPU usage has been above 90% for more than 5 minutes."
      },
      "startsAt": "2024-01-01T10:00:00Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "fingerprint": "abc123def456"
    }]
  }'

# Wait a moment, then send the RESOLVED alert
curl -X POST http://localhost:8000/webhook/alertmanager \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "alerts": [{
      "status": "resolved",
      "labels": {
        "alertname": "HighCPUUsage",
        "instance": "node-1",
        "severity": "critical"
      },
      "annotations": {
        "summary": "CPU usage is back to normal on node-1"
      },
      "startsAt": "2024-01-01T10:00:00Z",
      "endsAt": "2024-01-01T10:12:34Z",
      "fingerprint": "abc123def456"
    }]
  }'
```

The original Slack message will be updated in-place from 🔴 FIRING → ✅ RESOLVED, and a thread reply will show the resolution duration.

---

## 📡 Webhook Endpoints

| Endpoint | Source | Description |
|----------|--------|-------------|
| `POST /webhook/alertmanager` | Prometheus Alertmanager | Standard Alertmanager webhook receiver |
| `POST /webhook/grafana` | Grafana Unified Alerting | Grafana contact point webhook |
| `POST /webhook/cloudwatch` | AWS CloudWatch (via SNS) | CloudWatch Alarm → SNS → webhook |
| `POST /webhook/opensearch` | OpenSearch Alerting | OpenSearch monitor notification |
| `POST /webhook/generic` | Auto-detect | Automatically detects the source format |
| `GET /health` | — | Liveness probe (always OK if running) |
| `GET /ready` | — | Readiness probe (checks Redis connection) |
| `GET /metrics` | — | Prometheus-format metrics |

---

## ⚙️ Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | **(required)** | Slack Bot OAuth token (`xoxb-...`) |
| `SLACK_DEFAULT_CHANNEL` | `#alerts` | Default Slack channel |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `REDIS_TTL_SECONDS` | `604800` (7 days) | TTL for alert state in Redis |
| `DEDUP_WINDOW_SECONDS` | `300` (5 min) | Window to suppress duplicate firings |
| `RESOLVE_UPDATE_ORIGINAL` | `true` | Update original message on resolution |
| `RESOLVE_THREAD_REPLY` | `true` | Post thread reply on resolution |
| `WEBHOOK_SECRET` | *(empty)* | Optional shared secret for webhook auth |
| `LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |
| `ENVIRONMENT` | `production` | Environment name |

---

## 🔧 Source Configuration

### Prometheus Alertmanager

Add this to your `alertmanager.yml`:

```yaml
receivers:
  - name: 'alert-middleware'
    webhook_configs:
      - url: 'http://alert-middleware-svc.alert-middleware:80/webhook/alertmanager'
        send_resolved: true  # ← Required for resolution correlation!

route:
  receiver: 'alert-middleware'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
```

### Grafana Unified Alerting

1. Go to **Alerting → Contact Points → New Contact Point**
2. Type: **Webhook**
3. URL: `http://alert-middleware-svc.alert-middleware:80/webhook/grafana`
4. Enable **Send resolved** ✅

### AWS CloudWatch (via SNS)

1. Create an SNS topic
2. Add an HTTPS subscription pointing to your middleware:
   `https://alerts-webhook.example.com/webhook/cloudwatch`
3. Configure your CloudWatch Alarm to send to the SNS topic
4. Ensure the alarm sends both `ALARM` and `OK` states

### OpenSearch Alerting

1. Go to **Alerting → Destinations → Create Destination**
2. Type: **Custom webhook**
3. URL: `http://alert-middleware-svc.alert-middleware:80/webhook/opensearch`
4. Configure your monitors to use this destination

---

## 🚢 Deployment

### Option A: Helm Chart (Recommended)

```bash
# Install
helm install alert-middleware ./helm/alert-middleware \
  --namespace alert-middleware \
  --create-namespace \
  --set secrets.slackBotToken="xoxb-your-token" \
  --set config.slackDefaultChannel="#alerts"

# Install with ingress
helm install alert-middleware ./helm/alert-middleware \
  --namespace alert-middleware \
  --create-namespace \
  --set secrets.slackBotToken="xoxb-your-token" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=alerts-webhook.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix

# Upgrade
helm upgrade alert-middleware ./helm/alert-middleware \
  --namespace alert-middleware \
  --reuse-values \
  --set image.tag="1.1.0"

# Uninstall
helm uninstall alert-middleware -n alert-middleware
```

#### Production values override (`values-prod.yaml`):

```yaml
replicaCount: 3
autoscaling:
  minReplicas: 3
  maxReplicas: 15
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi
redis:
  persistence:
    size: 5Gi
config:
  logLevel: "WARNING"
  environment: "production"
```

```bash
helm install alert-middleware ./helm/alert-middleware \
  -f values-prod.yaml \
  --set secrets.slackBotToken="$SLACK_BOT_TOKEN"
```

### Option B: Kustomize

```bash
# Dev environment
kubectl apply -k k8s/overlays/dev

# Production environment
kubectl apply -k k8s/overlays/prod

# Before applying, edit the secret:
# echo -n 'xoxb-your-token' | base64
# Update k8s/base/secret.yaml with the base64-encoded value
```

### Option C: Raw Manifests

```bash
# Apply base manifests directly
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/

# ⚠️ Remember to update secret.yaml first!
```

---

## 📊 Monitoring

The middleware exposes Prometheus metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `acm_alerts_received_total` | Counter | Total alerts received |
| `acm_alerts_firing_total` | Counter | Total firing alerts |
| `acm_alerts_resolved_total` | Counter | Total resolved alerts |
| `acm_alerts_deduplicated_total` | Counter | Alerts suppressed by dedup |
| `acm_alerts_errors_total` | Counter | Processing errors |
| `acm_webhook_requests_total` | Counter | Total webhook requests |
| `acm_webhook_latency_seconds_sum` | Gauge | Cumulative processing latency |

The K8s deployment includes Prometheus scrape annotations:
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: "/metrics"
```

---

## 🏗️ Project Structure

```
alert-correlation-middleware/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Pydantic-settings configuration
│   ├── constants.py              # Shared constants
│   ├── logging_config.py         # Structured JSON logging
│   ├── main.py                   # FastAPI app + webhook endpoints
│   ├── models.py                 # NormalizedAlert & AlertState models
│   ├── normalizers/
│   │   ├── __init__.py
│   │   ├── alertmanager.py       # Prometheus Alertmanager normalizer
│   │   ├── cloudwatch.py         # AWS CloudWatch normalizer
│   │   ├── fingerprint.py        # Consistent fingerprint generation
│   │   ├── grafana.py            # Grafana Unified Alerting normalizer
│   │   └── opensearch.py         # OpenSearch Alerting normalizer
│   └── services/
│       ├── __init__.py
│       ├── processor.py          # Core alert processing engine
│       ├── redis_store.py        # Redis state management
│       └── slack_client.py       # Slack API integration
├── k8s/
│   ├── base/                     # Base Kubernetes manifests
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   ├── networkpolicy.yaml
│   │   ├── ingress.yaml
│   │   ├── redis-deployment.yaml
│   │   ├── redis-service.yaml
│   │   └── redis-pvc.yaml
│   └── overlays/
│       ├── dev/                  # Dev: single replica, debug logging
│       └── prod/                 # Prod: 3 replicas, larger resources
├── helm/
│   └── alert-middleware/         # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── Dockerfile                    # Multi-stage, non-root image
├── docker-compose.yml            # Local dev: app + Redis
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .dockerignore
└── README.md
```

---

## 🔐 Security

| Feature | Implementation |
|---------|---------------|
| **Non-root container** | Runs as UID 1000 with read-only filesystem |
| **Webhook auth** | Optional `Bearer` token via `WEBHOOK_SECRET` |
| **Network policy** | Only allows ingress on port 8000, egress to Redis + Slack |
| **Pod security** | `allowPrivilegeEscalation: false`, all capabilities dropped |
| **Secret management** | Supports existing K8s Secrets, Sealed Secrets, or Vault |
| **TLS** | Ingress-level TLS termination |

---

## 🧩 Adding a New Alert Source

1. Create `app/normalizers/yoursource.py`:
   - Accept the raw payload `Dict[str, Any]`
   - Return `List[NormalizedAlert]`
   - Use `generate_fingerprint()` for consistent correlation

2. Register in `app/normalizers/__init__.py`

3. Add a constant in `app/constants.py`

4. Add the endpoint in `app/main.py`:
   ```python
   @app.post("/webhook/yoursource")
   async def webhook_yoursource(request: Request, ...):
       payload = await request.json()
       return await _process_webhook("yoursource", payload, authorization)
   ```

5. Update `_NORMALIZERS` and `_detect_source()` in `main.py`

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push and open a PR

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
