# Chapter 6: Values & Configuration Mastery ⚙️

## 🟡 INTERMEDIATE LEVEL

---

## 🎯 The Values System — How Configuration Flows

```
╔══════════════════════════════════════════════════════════════════════╗
║                   VALUES MERGE ORDER                                ║
║           (Later sources OVERRIDE earlier ones)                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  LOWEST PRIORITY                                                     ║
║  ┌────────────────────────────┐                                     ║
║  │ 1. Subchart values.yaml   │  ← Dependency's defaults            ║
║  └────────────┬───────────────┘                                     ║
║               ▼                                                      ║
║  ┌────────────────────────────┐                                     ║
║  │ 2. Parent values.yaml     │  ← Your chart's defaults            ║
║  └────────────┬───────────────┘                                     ║
║               ▼                                                      ║
║  ┌────────────────────────────┐                                     ║
║  │ 3. -f values file #1      │  ← First values file                ║
║  └────────────┬───────────────┘                                     ║
║               ▼                                                      ║
║  ┌────────────────────────────┐                                     ║
║  │ 4. -f values file #2      │  ← Second file overrides first     ║
║  └────────────┬───────────────┘                                     ║
║               ▼                                                      ║
║  ┌────────────────────────────┐                                     ║
║  │ 5. --set / --set-string   │  ← CLI overrides (highest!)        ║
║  └────────────────────────────┘                                     ║
║  HIGHEST PRIORITY                                                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 📝 values.yaml Best Practices

### Organize with Clear Sections

```yaml
# ═══════════════════════════════════════════════════════════
# values.yaml — Well-organized example
# ═══════════════════════════════════════════════════════════

# ──────────── Global Settings ────────────
global:
  imageRegistry: ""            # Override for all charts
  imagePullSecrets: []
  storageClass: ""

# ──────────── Application ────────────
replicaCount: 2

image:
  repository: myorg/my-app
  tag: ""                       # Defaults to appVersion
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

# ──────────── Service Account ────────────
serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use
  name: ""

# ──────────── Pod Configuration ────────────
podAnnotations: {}
podLabels: {}

podSecurityContext:
  fsGroup: 1000

securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL

# ──────────── Service ────────────
service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  annotations: {}

# ──────────── Ingress ────────────
ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

# ──────────── Resources ────────────
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

# ──────────── Autoscaling ────────────
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# ──────────── Health Checks ────────────
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5

# ──────────── Volumes ────────────
volumes: []
volumeMounts: []

# ──────────── Scheduling ────────────
nodeSelector: {}
tolerations: []
affinity: {}

# ──────────── Application Config ────────────
config:
  logLevel: "info"
  port: 8080
  features:
    enableMetrics: true
    enableTracing: false

# ──────────── Dependencies ────────────
postgresql:
  enabled: true
  auth:
    postgresPassword: "changeme"
    database: "myappdb"

redis:
  enabled: false
```

---

## 🌍 Multi-Environment Strategy

```
┌──────────────────────────────────────────────────────────────────┐
│               MULTI-ENVIRONMENT PATTERN                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📁 my-chart/                                                    │
│  ├── Chart.yaml                                                  │
│  ├── values.yaml              ← Shared defaults                 │
│  ├── values-dev.yaml          ← Dev overrides                   │
│  ├── values-staging.yaml      ← Staging overrides               │
│  └── values-prod.yaml         ← Production overrides            │
│                                                                  │
│  Deploy to dev:                                                  │
│  helm install my-app ./my-chart -f values-dev.yaml              │
│                                                                  │
│  Deploy to staging:                                              │
│  helm install my-app ./my-chart -f values-staging.yaml          │
│                                                                  │
│  Deploy to prod:                                                 │
│  helm install my-app ./my-chart -f values-prod.yaml             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Example Environment Files:

```yaml
# ═══════════════════════════════════════════════════════
# values-dev.yaml — Development environment
# ═══════════════════════════════════════════════════════
replicaCount: 1

image:
  tag: "latest"
  pullPolicy: Always

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 50m
    memory: 64Mi

config:
  logLevel: "debug"
  features:
    enableMetrics: false
    enableTracing: true     # Debug tracing in dev

ingress:
  enabled: true
  hosts:
    - host: myapp.dev.local
      paths:
        - path: /
          pathType: Prefix

postgresql:
  auth:
    postgresPassword: "devpassword"
```

```yaml
# ═══════════════════════════════════════════════════════
# values-staging.yaml — Staging environment
# ═══════════════════════════════════════════════════════
replicaCount: 2

image:
  tag: "rc-1.5.0"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

config:
  logLevel: "info"

ingress:
  enabled: true
  hosts:
    - host: myapp.staging.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: staging-tls
      hosts:
        - myapp.staging.example.com
```

```yaml
# ═══════════════════════════════════════════════════════
# values-prod.yaml — Production environment
# ═══════════════════════════════════════════════════════
replicaCount: 5

image:
  tag: "1.5.0"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: "1"
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

config:
  logLevel: "warn"
  features:
    enableMetrics: true
    enableTracing: true

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: prod-tls
      hosts:
        - myapp.example.com

podDisruptionBudget:
  enabled: true
  minAvailable: 3

postgresql:
  auth:
    existingSecret: "prod-db-credentials"
  primary:
    persistence:
      size: 100Gi
```

### Visual Comparison:

```
┌─────────────────┬───────────────┬───────────────┬───────────────┐
│   Setting       │     DEV       │   STAGING     │   PRODUCTION  │
├─────────────────┼───────────────┼───────────────┼───────────────┤
│ Replicas        │      1        │      2        │      5+       │
│ Image tag       │   latest      │   rc-1.5.0    │    1.5.0      │
│ CPU limit       │   200m        │   500m        │    1 core     │
│ Memory limit    │   256Mi       │   512Mi       │    1Gi        │
│ Log level       │   debug       │   info        │    warn       │
│ Autoscaling     │   ❌ off      │   ❌ off      │   ✅ on       │
│ TLS             │   ❌ off      │   ✅ on       │   ✅ on       │
│ DB password     │   plaintext   │   plaintext   │   K8s Secret  │
│ PDB             │   ❌ off      │   ❌ off      │   ✅ on       │
│ Rate limiting   │   ❌ off      │   ❌ off      │   ✅ on       │
└─────────────────┴───────────────┴───────────────┴───────────────┘
```

---

## 🔧 --set Syntax Deep Dive

```bash
# ═══════════════════════════════════════════════════════
# SIMPLE VALUES
# ═══════════════════════════════════════════════════════
--set replicaCount=5
--set image.tag=v2.0
--set service.type=NodePort

# ═══════════════════════════════════════════════════════
# STRING VALUES (force string type)
# ═══════════════════════════════════════════════════════
--set-string image.tag=1.0     # "1.0" not number 1
--set image.tag="1.0"          # Also works with quotes

# ═══════════════════════════════════════════════════════
# NESTED VALUES (dots = nesting)
# ═══════════════════════════════════════════════════════
--set a.b.c=hello
# Equivalent YAML:
# a:
#   b:
#     c: hello

# ═══════════════════════════════════════════════════════
# MULTIPLE VALUES
# ═══════════════════════════════════════════════════════
--set replicaCount=3,service.port=8080
# or
--set replicaCount=3 --set service.port=8080

# ═══════════════════════════════════════════════════════
# LISTS / ARRAYS
# ═══════════════════════════════════════════════════════
--set servers[0].port=80
--set servers[0].host=web1
--set servers[1].port=81
# Equivalent YAML:
# servers:
#   - port: 80
#     host: web1
#   - port: 81

# ═══════════════════════════════════════════════════════
# SPECIAL CHARACTERS (escape with \)
# ═══════════════════════════════════════════════════════
--set "nodeSelector.kubernetes\.io/os=linux"
# Equivalent YAML:
# nodeSelector:
#   kubernetes.io/os: linux

# ═══════════════════════════════════════════════════════
# NULL / EMPTY (to reset/remove a value)
# ═══════════════════════════════════════════════════════
--set ingress=null
--set annotations=null

# ═══════════════════════════════════════════════════════
# FROM FILE (--set-file)
# ═══════════════════════════════════════════════════════
--set-file sshKey=~/.ssh/id_rsa.pub
# Loads file content as the value

# ═══════════════════════════════════════════════════════
# JSON VALUES (--set-json)
# ═══════════════════════════════════════════════════════
--set-json 'resources={"limits":{"cpu":"1","memory":"1Gi"}}'
```

---

## 🌐 Global Values

```yaml
# ═══════════════════════════════════════════════════════
# Global values are shared with ALL sub-charts
# ═══════════════════════════════════════════════════════

# Parent chart values.yaml:
global:
  imageRegistry: myregistry.example.com
  imagePullSecrets:
    - name: my-registry-secret
  storageClass: fast-ssd

# In parent chart template:
image: {{ .Values.global.imageRegistry }}/myapp:v1

# In subchart template (same access!):
image: {{ .Values.global.imageRegistry }}/postgres:14
```

```
How Global Values Flow:
━━━━━━━━━━━━━━━━━━━━━━

  Parent Chart (values.yaml)
  ┌──────────────────────────────┐
  │ global:                      │
  │   imageRegistry: myregistry  │──────┐
  │                              │      │
  │ replicaCount: 3              │      │
  │ (only for parent)            │      │
  └──────────────────────────────┘      │
                                        │
          ┌─────────────────────────────┤
          │                             │
          ▼                             ▼
  ┌───────────────────┐   ┌───────────────────┐
  │ Sub-chart:        │   │ Sub-chart:        │
  │ postgresql        │   │ redis             │
  │                   │   │                   │
  │ Can access:       │   │ Can access:       │
  │ .Values.global    │   │ .Values.global    │
  │ .imageRegistry ✅ │   │ .imageRegistry ✅ │
  │                   │   │                   │
  │ Cannot access:    │   │ Cannot access:    │
  │ parent's          │   │ parent's          │
  │ .replicaCount ❌  │   │ .replicaCount ❌  │
  └───────────────────┘   └───────────────────┘
  
  Global = shared everywhere
  Non-global = stays in parent
```

---

## 🔐 Handling Secrets in Values

```
┌──────────────────────────────────────────────────────────────────┐
│                 SECRETS MANAGEMENT STRATEGIES                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ❌ BAD: Plaintext secrets in values.yaml                       │
│                                                                  │
│     database:                                                    │
│       password: "super-secret-123"    ← In Git! Dangerous!     │
│                                                                  │
│  ✅ OPTION 1: --set at deploy time                              │
│                                                                  │
│     helm install my-app ./chart \                               │
│       --set database.password=$DB_PASSWORD                      │
│     (password from CI/CD env variable)                          │
│                                                                  │
│  ✅ OPTION 2: External Secrets (K8s Secret reference)           │
│                                                                  │
│     # values.yaml                                               │
│     database:                                                    │
│       existingSecret: "my-db-credentials"                       │
│       existingSecretKey: "password"                              │
│                                                                  │
│     # template uses:                                             │
│     valueFrom:                                                   │
│       secretKeyRef:                                              │
│         name: {{ .Values.database.existingSecret }}              │
│         key: {{ .Values.database.existingSecretKey }}            │
│                                                                  │
│  ✅ OPTION 3: Helm Secrets plugin (sops encryption)             │
│                                                                  │
│     helm secrets install my-app ./chart \                       │
│       -f secrets.yaml.enc                                       │
│     (encrypted at rest, decrypted during deploy)                │
│                                                                  │
│  ✅ OPTION 4: External Secrets Operator                         │
│                                                                  │
│     Syncs secrets from AWS Secrets Manager, Vault, etc.         │
│     into Kubernetes Secrets automatically                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### ExistingSecret Pattern (Recommended):

```yaml
# values.yaml
database:
  # Option A: Let chart create secret (dev/testing)
  password: ""
  
  # Option B: Use pre-created K8s secret (production)
  existingSecret: ""
  existingSecretPasswordKey: "password"

# templates/deployment.yaml
env:
  - name: DB_PASSWORD
    {{- if .Values.database.existingSecret }}
    valueFrom:
      secretKeyRef:
        name: {{ .Values.database.existingSecret }}
        key: {{ .Values.database.existingSecretPasswordKey | default "password" }}
    {{- else }}
    valueFrom:
      secretKeyRef:
        name: {{ include "my-chart.fullname" . }}-db
        key: password
    {{- end }}
```

---

## 🔍 Inspecting & Debugging Values

```bash
# ═══════════════════════════════════════════════════════
# See chart's default values
# ═══════════════════════════════════════════════════════
helm show values bitnami/nginx

# ═══════════════════════════════════════════════════════
# See ACTUAL values used by a deployed release
# ═══════════════════════════════════════════════════════
helm get values my-app

# See ALL values (including defaults)
helm get values my-app --all

# Output as JSON
helm get values my-app -o json

# ═══════════════════════════════════════════════════════
# Preview merged values (dry-run)
# ═══════════════════════════════════════════════════════
helm install my-app ./chart \
  -f values-prod.yaml \
  --set replicaCount=10 \
  --dry-run --debug 2>&1 | head -100

# ═══════════════════════════════════════════════════════
# Compare values between revisions
# ═══════════════════════════════════════════════════════
helm get values my-app --revision 1 > rev1-values.yaml
helm get values my-app --revision 2 > rev2-values.yaml
diff rev1-values.yaml rev2-values.yaml
```

---

## 🧠 Knowledge Check

```
Q1: What's the priority order for values?
A:  chart defaults < parent chart < -f file(s) < --set
    (--set always wins)

Q2: How do you pass values for sub-charts?
A:  Under the subchart's name in parent values.yaml:
    postgresql:
      auth:
        password: "xxx"

Q3: What are global values?
A:  Values under the 'global:' key that are accessible
    by ALL charts (parent and sub-charts).

Q4: How should you handle secrets in production?
A:  Use existingSecret pattern, external secrets operator,
    or pass via --set from CI/CD environment variables.
    NEVER commit plaintext secrets to Git.

Q5: How do you see values used by a deployed release?
A:  helm get values <release-name>
    Add --all for defaults too.
```

---

**Next → [Chapter 7: Helm Commands Mastery](07-commands.md)** ➡️
