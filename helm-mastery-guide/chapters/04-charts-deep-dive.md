# Chapter 4: Charts Deep Dive 📦

## 🟡 INTERMEDIATE LEVEL

---

## 📁 Chart Directory Structure — Every File Explained

```
📦 my-awesome-app/
│
│  ════════════════════════════════════════════════════════
│  REQUIRED FILES
│  ════════════════════════════════════════════════════════
│
├── 📄 Chart.yaml            ★ The chart's identity card
│                               Defines name, version, deps
│
├── 📄 values.yaml           ★ Default configuration values
│                               Users override these
│
├── 📁 templates/            ★ Kubernetes resource templates
│   │
│   │  ─────── Core Resources ───────
│   ├── 📄 deployment.yaml       Pod controller
│   ├── 📄 service.yaml          Network exposure
│   ├── 📄 ingress.yaml          External routing
│   ├── 📄 configmap.yaml        Configuration data
│   ├── 📄 secret.yaml           Sensitive data
│   ├── 📄 hpa.yaml              Auto-scaling
│   ├── 📄 serviceaccount.yaml   RBAC identity
│   ├── 📄 pvc.yaml              Storage claims
│   │
│   │  ─────── Special Files ───────
│   ├── 📄 _helpers.tpl         Template helper functions
│   │                            (starts with _ = not rendered)
│   │
│   ├── 📄 NOTES.txt            Post-install instructions
│   │                            (displayed after helm install)
│   │
│   └── 📁 tests/               Helm test definitions
│       └── 📄 test-connection.yaml
│
│  ════════════════════════════════════════════════════════
│  OPTIONAL FILES
│  ════════════════════════════════════════════════════════
│
├── 📁 charts/               Sub-charts (dependencies)
│   ├── 📦 postgresql-12.1.2.tgz
│   └── 📦 redis-17.3.4.tgz
│
├── 📁 crds/                 Custom Resource Definitions
│   └── 📄 my-crd.yaml        (installed BEFORE templates)
│
├── 📄 Chart.lock            Dependency lock file (auto-gen)
├── 📄 .helmignore           Files to exclude from packaging
├── 📄 README.md             Documentation
├── 📄 LICENSE               License info
└── 📄 values.schema.json    JSON Schema for values validation
```

---

## 📄 Chart.yaml — The Identity Card

```yaml
# ═══════════════════════════════════════════════════════════
# Chart.yaml — REQUIRED (The most important file)
# ═══════════════════════════════════════════════════════════

# API version (always v2 for Helm 3)
apiVersion: v2

# Chart name (must match directory name)
name: my-awesome-app

# Human-readable description
description: A Helm chart for My Awesome Web Application

# Chart type: "application" or "library"
#   application → can be installed (default)
#   library    → provides helpers to other charts, can't be installed alone
type: application

# ┌──────────────────────────────────────────────────────┐
# │  TWO DIFFERENT VERSIONS — Don't confuse them!        │
# │                                                      │
# │  version:    "1.2.3"   ← Chart package version      │
# │                          Changes when chart changes  │
# │                          Follows SemVer              │
# │                                                      │
# │  appVersion: "4.5.6"   ← App inside the chart       │
# │                          The actual software version │
# │                          (nginx 1.27, redis 7.2)     │
# └──────────────────────────────────────────────────────┘
version: 1.2.3
appVersion: "4.5.6"

# Keywords for searching
keywords:
  - web
  - nginx
  - http

# Project homepage
home: https://github.com/myorg/my-awesome-app

# Project source repositories
sources:
  - https://github.com/myorg/my-awesome-app

# Maintainers
maintainers:
  - name: John Doe
    email: john@example.com
    url: https://johndoe.dev

# Icon URL (shows in Artifact Hub)
icon: https://example.com/icon.png

# Annotations (custom metadata)
annotations:
  category: WebApplication

# ═══════════════════════════════════════════════════════════
# DEPENDENCIES (other charts this chart needs)
# ═══════════════════════════════════════════════════════════
dependencies:
  - name: postgresql
    version: "12.x.x"           # SemVer range
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled  # Toggle on/off via values
    tags:
      - database

  - name: redis
    version: "~17.3"            # ~17.3 = >=17.3.0, <17.4.0
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    alias: cacheStore           # Rename in this chart
    tags:
      - cache

# Minimum Kubernetes version required
kubeVersion: ">=1.24.0-0"

# Deprecation notice
deprecated: false
```

### Version vs AppVersion Visualized:

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Chart: nginx-chart                                          │
│                                                              │
│  version: 1.0.0    ← You update Chart.yaml templates        │
│  appVersion: 1.25  ← Nginx 1.25 inside                      │
│       │                                                      │
│       ▼                                                      │
│  version: 1.1.0    ← Added new template (ingress)           │
│  appVersion: 1.25  ← Still Nginx 1.25 (app didn't change)   │
│       │                                                      │
│       ▼                                                      │
│  version: 1.1.1    ← Fixed a bug in template                │
│  appVersion: 1.25  ← Still Nginx 1.25                        │
│       │                                                      │
│       ▼                                                      │
│  version: 2.0.0    ← Breaking changes in values             │
│  appVersion: 1.27  ← Upgraded to Nginx 1.27                 │
│                                                              │
│  SemVer for chart version:                                   │
│  MAJOR.MINOR.PATCH                                           │
│  2    .0    .0                                               │
│  │     │     └── Bug fixes                                   │
│  │     └──────── New features, backward compatible           │
│  └────────────── Breaking changes                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📄 values.yaml — The Configuration Hub

```yaml
# ═══════════════════════════════════════════════════════════
# values.yaml — Default configuration
# ═══════════════════════════════════════════════════════════
# Users override these values via:
#   helm install ... -f custom-values.yaml
#   helm install ... --set key=value

# ──────── Replica Configuration ────────
replicaCount: 2

# ──────── Container Image ────────
image:
  repository: myorg/my-awesome-app
  tag: ""          # Defaults to chart appVersion
  pullPolicy: IfNotPresent

# Image pull secrets for private registries
imagePullSecrets: []
  # - name: my-registry-secret

# ──────── Service Configuration ────────
service:
  type: ClusterIP            # ClusterIP, NodePort, LoadBalancer
  port: 80
  targetPort: 8080
  annotations: {}

# ──────── Ingress Configuration ────────
ingress:
  enabled: false             # Toggle on/off
  className: "nginx"
  annotations: {}
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []
    # - secretName: myapp-tls
    #   hosts:
    #     - myapp.example.com

# ──────── Resource Limits ────────
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

# ──────── Autoscaling ────────
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# ──────── Health Checks ────────
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5

# ──────── Node Selection ────────
nodeSelector: {}
tolerations: []
affinity: {}

# ──────── Dependencies Toggle ────────
postgresql:
  enabled: true
  auth:
    postgresPassword: "changeme"
    database: "myappdb"

redis:
  enabled: false
```

### Values Priority (Override Order):

```
Priority: LOW ──────────────────────────────────────→ HIGH

┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌───────────┐
│   Chart's   │   │ Parent      │   │ -f / --values│   │  --set    │
│ values.yaml │ < │ chart vals  │ < │  file(s)     │ < │  flags    │
│  (defaults) │   │(if subchart)│   │              │   │           │
└─────────────┘   └─────────────┘   └─────────────┘   └───────────┘

Example:
  values.yaml:     replicaCount: 2      ← default
  prod.yaml:       replicaCount: 5      ← file override
  --set:           replicaCount=10      ← CLI override (wins!)

  Final value: replicaCount = 10
```

---

## 🏗️ Creating Your First Chart

### Method 1: `helm create` (Scaffolding)

```bash
# Generate a new chart with boilerplate
helm create my-first-chart
```

```
What gets generated:
━━━━━━━━━━━━━━━━━━━━

my-first-chart/
├── .helmignore          # Patterns to ignore when packaging
├── Chart.yaml           # Pre-filled chart metadata
├── values.yaml          # Sensible defaults for nginx
├── charts/              # Empty, for dependencies
└── templates/
    ├── deployment.yaml  # Full deployment template
    ├── service.yaml     # Service template
    ├── ingress.yaml     # Ingress template (disabled by default)
    ├── hpa.yaml         # HPA template (disabled by default)
    ├── serviceaccount.yaml
    ├── _helpers.tpl     # Template helper functions
    ├── NOTES.txt        # Post-install notes
    └── tests/
        └── test-connection.yaml

This is a FULLY WORKING nginx chart! 🎉
You can install it immediately:

  helm install test ./my-first-chart
```

### Method 2: From Scratch (Minimal Chart)

```bash
# Create minimal chart structure
mkdir -p my-minimal-chart/templates

# Create Chart.yaml (REQUIRED)
cat > my-minimal-chart/Chart.yaml << 'EOF'
apiVersion: v2
name: my-minimal-chart
description: A minimal Helm chart
version: 0.1.0
appVersion: "1.0.0"
EOF

# Create a simple template
cat > my-minimal-chart/templates/configmap.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  greeting: "Hello from Helm!"
EOF

# That's it! This is a valid chart!
helm install test-minimal ./my-minimal-chart
```

```
Minimal chart structure:
━━━━━━━━━━━━━━━━━━━━━━━━

my-minimal-chart/
├── Chart.yaml              ← Required
└── templates/
    └── configmap.yaml      ← At least one template

Only 2 files needed for a valid chart!
(values.yaml is technically optional)
```

---

## 📦 Chart Types: Application vs Library

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  APPLICATION CHART (type: application)                           │
│  ════════════════════════════════════                             │
│                                                                  │
│  ✅ Can be installed directly                                    │
│  ✅ Creates Kubernetes resources                                 │
│  ✅ Can have dependencies                                       │
│  ✅ This is the DEFAULT type                                    │
│                                                                  │
│  Example: nginx chart, postgresql chart, your-app chart         │
│                                                                  │
│  helm install my-app ./my-application-chart  ← Works!           │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LIBRARY CHART (type: library)                                   │
│  ═══════════════════════════                                     │
│                                                                  │
│  ❌ CANNOT be installed directly                                │
│  ❌ CANNOT create resources on its own                          │
│  ✅ Provides reusable template helpers                          │
│  ✅ Is used as a dependency by application charts               │
│                                                                  │
│  Example: common utility functions shared across charts          │
│                                                                  │
│  helm install my-lib ./my-library-chart  ← ERROR!               │
│                                                                  │
│  How it's used:                                                  │
│  ┌────────────────────────────────────┐                         │
│  │ # In application chart's Chart.yaml│                         │
│  │ dependencies:                      │                         │
│  │   - name: common                   │                         │
│  │     version: 1.x.x                │                         │
│  │     repository: "https://..."      │                         │
│  └────────────────────────────────────┘                         │
│                                                                  │
│  Then use its functions:                                         │
│  {{ include "common.labels" . }}                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Dependencies Management

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    
  - name: redis  
    version: "~17.3"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    alias: cache
```

### Dependency Commands:

```bash
# Download dependencies into charts/ directory
helm dependency update ./my-chart
# or short form:
helm dep up ./my-chart

# List dependencies and their status
helm dependency list ./my-chart

# Rebuild the charts/ directory
helm dependency build ./my-chart
```

### How Dependencies Work:

```
BEFORE: helm dependency update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

my-chart/
├── Chart.yaml       (lists postgresql & redis as deps)
├── charts/          (EMPTY!)
└── templates/


AFTER: helm dependency update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

my-chart/
├── Chart.yaml
├── Chart.lock       ← NEW! Locks exact versions
├── charts/
│   ├── postgresql-12.1.2.tgz   ← Downloaded!
│   └── redis-17.3.4.tgz        ← Downloaded!
└── templates/


When you helm install:
━━━━━━━━━━━━━━━━━━━━━

  helm install my-app ./my-chart
      │
      ├── Installs my-chart resources
      ├── Installs postgresql resources
      └── Installs redis resources
      
  All in ONE release! All managed together!
```

### Dependency Conditions & Tags:

```yaml
# values.yaml
postgresql:
  enabled: true      # ← This controls the 'condition'
redis:
  enabled: false     # ← Redis will NOT be installed

tags:
  database: true     # ← Install all deps tagged 'database'
  cache: false       # ← Skip all deps tagged 'cache'
```

```
Condition vs Tags:
━━━━━━━━━━━━━━━━━━

  condition: Checks a specific values path (boolean)
             "postgresql.enabled" → values.postgresql.enabled
             
  tags:      Group multiple dependencies
             tag: "database" → all deps with this tag
             
  Priority:  condition OVERRIDES tags
```

---

## 📦 Packaging & Distribution

```bash
# Package your chart into a .tgz file
helm package ./my-chart

# Output: my-chart-1.2.3.tgz

# Package with a different destination
helm package ./my-chart --destination ./releases/

# Package with specific version override
helm package ./my-chart --version 2.0.0

# Package with app-version override
helm package ./my-chart --app-version 5.0.0
```

```
What's inside the .tgz?
━━━━━━━━━━━━━━━━━━━━━━━

my-chart-1.2.3.tgz
├── my-chart/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ...
│   ├── charts/         (includes downloaded deps)
│   └── README.md

Files in .helmignore are EXCLUDED.
```

### .helmignore Example:

```
# .helmignore — Like .gitignore but for Helm packaging

# Common patterns
.git
.gitignore
.idea/
*.swp
*.bak
*.tmp
.DS_Store

# CI/CD files
.github/
.gitlab-ci.yml
Jenkinsfile

# Test files  
tests/
*_test.go

# Documentation that doesn't need to be in the package
docs/
CONTRIBUTING.md
```

---

## ✅ values.schema.json — Validating Values

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount", "image"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "description": "Number of pod replicas"
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {
          "type": "string",
          "description": "Container image repository"
        },
        "tag": {
          "type": "string",
          "description": "Container image tag"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    },
    "service": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ClusterIP", "NodePort", "LoadBalancer"]
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    }
  }
}
```

```
What happens with schema validation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  helm install my-app ./my-chart --set replicaCount=-5

  ❌ ERROR: values don't meet the specifications of the
            schema(s):
  - replicaCount: Must be >= 1

  helm install my-app ./my-chart --set service.type=Magic

  ❌ ERROR: values don't meet the specifications of the
            schema(s):  
  - service.type: Must be one of: ClusterIP, NodePort, LoadBalancer
  
  Catches mistakes BEFORE deploying! 🛡️
```

---

## 📝 NOTES.txt — Post-Install Instructions

```
{{/* templates/NOTES.txt */}}

╔══════════════════════════════════════════════════════════╗
║  🎉 {{ .Chart.Name }} has been deployed!                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Release:   {{ .Release.Name }}                          ║
║  Namespace: {{ .Release.Namespace }}                     ║
║  Status:    Deployed                                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

{{- if .Values.ingress.enabled }}
Access your application at:
{{- range .Values.ingress.hosts }}
  http://{{ .host }}
{{- end }}
{{- else }}
Get the application URL by running:
  kubectl port-forward svc/{{ include "my-chart.fullname" . }} \
    {{ .Values.service.port }}:{{ .Values.service.port }}
  
  Then visit: http://localhost:{{ .Values.service.port }}
{{- end }}
```

```
This shows up after helm install:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$ helm install my-app ./my-chart

NAME: my-app
STATUS: deployed

NOTES:
╔══════════════════════════════════════════════════════════╗
║  🎉 my-chart has been deployed!                         ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Release:   my-app                                       ║
║  Namespace: default                                      ║
║  Status:    Deployed                                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

Get the application URL by running:
  kubectl port-forward svc/my-app-my-chart 80:80
  
  Then visit: http://localhost:80
```

---

## 🧠 Knowledge Check

```
Q1: What are the only REQUIRED files in a chart?
A:  Chart.yaml and at least one file in templates/
    (values.yaml is technically optional but recommended)

Q2: What's the difference between chart version and appVersion?
A:  version = chart package version (your templates/config)
    appVersion = the application's version (nginx 1.27)

Q3: What does "type: library" mean in Chart.yaml?
A:  The chart provides reusable helpers but CANNOT be
    installed directly. Used as a dependency.

Q4: How do you download dependencies?
A:  helm dependency update ./my-chart
    (or helm dep up ./my-chart)

Q5: What does values.schema.json do?
A:  Validates values against a JSON Schema before install.
    Catches invalid configurations early.

Q6: What file should start with underscore in templates/?
A:  _helpers.tpl — The underscore tells Helm NOT to render
    it as a Kubernetes resource.
```

---

**Next → [Chapter 5: Templates & Go Templating](05-templates.md)** ➡️
