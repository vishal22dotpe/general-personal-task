# 📋 HELM CHEAT SHEET — Complete Quick Reference

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██╗  ██╗███████╗██╗     ███╗   ███╗                           ║
║   ██║  ██║██╔════╝██║     ████╗ ████║                           ║
║   ███████║█████╗  ██║     ██╔████╔██║                           ║
║   ██╔══██║██╔══╝  ██║     ██║╚██╔╝██║                           ║
║   ██║  ██║███████╗███████╗██║ ╚═╝ ██║                           ║
║   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝                           ║
║                                                                  ║
║            CHEAT SHEET v3.x                                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🔑 Core Concepts at a Glance

```
┌───────────┬──────────────────────────────────────────────────┐
│ Concept   │ Description                                      │
├───────────┼──────────────────────────────────────────────────┤
│ Chart     │ Package of K8s YAML templates + values            │
│ Release   │ Running instance of a chart on a cluster         │
│ Revision  │ Versioned snapshot of a release (install/upgrade)│
│ Repo      │ Where charts are stored (HTTP or OCI registry)   │
│ Values    │ Configuration that customizes a chart             │
│ Template  │ K8s YAML with {{ Go template }} placeholders     │
└───────────┴──────────────────────────────────────────────────┘
```

---

## ⚡ Most Used Commands

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 INSTALL / UPGRADE / DELETE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm install <release> <chart>                  # Install
helm install <release> <chart> -f values.yaml   # Install with values file
helm install <release> <chart> --set key=val    # Install with overrides
helm install <release> <chart> -n <ns> --create-namespace

helm upgrade <release> <chart>                  # Upgrade existing release
helm upgrade --install <release> <chart>        # Install or upgrade (CI/CD ✅)
helm upgrade <release> <chart> --atomic         # Auto-rollback on failure

helm rollback <release> [revision]              # Rollback to revision
helm uninstall <release>                        # Delete release

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 INSPECT & DEBUG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm list                                       # List all releases
helm list -A                                    # List across all namespaces
helm status <release>                           # Release status
helm history <release>                          # Revision history
helm get values <release>                       # Show values used
helm get values <release> --all                 # Show all values (+ defaults)
helm get manifest <release>                     # Show deployed YAML

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏗️ DEVELOP & TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm create <chart-name>                        # Scaffold new chart
helm template <release> <chart>                 # Render locally (no cluster)
helm template <release> <chart> -s templates/deployment.yaml  # Single file
helm lint <chart>                               # Check for errors
helm package <chart>                            # Create .tgz package
helm test <release>                             # Run chart tests

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📂 REPOSITORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm repo add <name> <url>                      # Add repo
helm repo update                                # Update repo index
helm repo list                                  # List repos
helm repo remove <name>                         # Remove repo
helm search repo <keyword>                      # Search added repos
helm search hub <keyword>                       # Search Artifact Hub
helm show values <chart>                        # Show chart's default values
helm show chart <chart>                         # Show Chart.yaml info

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 OCI REGISTRY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm registry login <registry>                  # Login
helm push <chart.tgz> oci://<registry>/<path>   # Push chart
helm pull oci://<registry>/<chart> --version X   # Pull chart
helm install <rel> oci://<reg>/<chart> --version X  # Install from OCI

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔗 DEPENDENCIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
helm dep update <chart>                         # Download deps
helm dep build <chart>                          # Build from lock file
helm dep list <chart>                           # Show deps
```

---

## 📁 Chart Structure

```
📦 my-chart/
├── Chart.yaml          ★ Chart metadata (REQUIRED)
├── values.yaml         ★ Default configuration
├── Chart.lock            Auto-generated dep lock
├── .helmignore           Files to exclude from package
├── values.schema.json    JSON schema for values validation
├── README.md             Documentation
│
├── templates/          ★ Kubernetes YAML templates
│   ├── _helpers.tpl      Named template functions (not rendered)
│   ├── NOTES.txt         Post-install instructions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   └── tests/
│       └── test-connection.yaml
│
├── charts/               Sub-charts (dependencies)
│   └── postgresql-12.1.2.tgz
│
└── crds/                 Custom Resource Definitions
```

---

## 📊 Built-in Objects

```
{{ .Values.xxx }}            ← Your values.yaml + overrides
{{ .Release.Name }}          ← Release name
{{ .Release.Namespace }}     ← Release namespace
{{ .Release.Revision }}      ← Revision number (1, 2, 3...)
{{ .Release.IsInstall }}     ← true if install (not upgrade)
{{ .Release.IsUpgrade }}     ← true if upgrade
{{ .Chart.Name }}            ← Chart name from Chart.yaml
{{ .Chart.Version }}         ← Chart version
{{ .Chart.AppVersion }}      ← App version
{{ .Template.Name }}         ← Current template file path
{{ .Capabilities.KubeVersion.Version }}  ← K8s version
{{ .Files.Get "file.txt" }} ← Read non-template file content
```

---

## 🔧 Template Syntax Quick Reference

### Basics
```yaml
{{ .Values.key }}                    # Value substitution
{{ .Values.key | quote }}            # Pipe to function
{{ .Values.key | default "fallback" | upper | quote }}  # Chain pipes
```

### Whitespace Control
```yaml
{{  normal  }}     # Keeps surrounding whitespace
{{- trim-left }}   # Eats whitespace/newlines BEFORE
{{ trim-right -}}  # Eats whitespace/newlines AFTER
{{- both sides -}} # Eats BOTH sides
```

### Conditionals
```yaml
{{- if .Values.enabled }}
  # rendered when truthy
{{- else if eq .Values.env "prod" }}
  # rendered when env is "prod"
{{- else }}
  # fallback
{{- end }}
```

### Comparison Operators
```
eq   ← equal             {{ if eq .Values.x "y" }}
ne   ← not equal         {{ if ne .Values.x "y" }}
lt   ← less than         {{ if lt .Values.x 5 }}
gt   ← greater than      {{ if gt .Values.x 10 }}
and  ← logical AND       {{ if and .Values.a .Values.b }}
or   ← logical OR        {{ if or .Values.a .Values.b }}
not  ← logical NOT       {{ if not .Values.disabled }}
```

### Loops
```yaml
# List iteration
{{- range .Values.items }}
- {{ . }}
{{- end }}

# Map iteration
{{- range $key, $value := .Values.env }}
{{ $key }}: {{ $value | quote }}
{{- end }}

# List with index
{{- range $index, $item := .Values.list }}
{{ $index }}: {{ $item }}
{{- end }}
```

### Scope Change (with)
```yaml
{{- with .Values.database }}
host: {{ .host }}              # . = .Values.database
release: {{ $.Release.Name }} # $ = root scope
{{- end }}
```

### Named Templates
```yaml
# Define in _helpers.tpl:
{{- define "my-chart.labels" -}}
app: {{ .Chart.Name }}
release: {{ .Release.Name }}
{{- end }}

# Use (always prefer include over template):
labels:
  {{- include "my-chart.labels" . | nindent 4 }}
```

### Variables
```yaml
{{- $name := .Values.name | default "app" -}}
{{- $fullName := printf "%s-%s" .Release.Name $name -}}
name: {{ $fullName }}
```

---

## 🔤 Most Used Functions

```
STRING:
  quote / squote        Wrap in double/single quotes
  upper / lower         UPPER / lower case
  title                 Title Case
  trim / trimSuffix / trimPrefix   Remove whitespace/suffix/prefix
  trunc N               Truncate to N characters
  replace OLD NEW       String replacement
  contains STR          Check if contains substring
  hasPrefix / hasSuffix Check prefix/suffix
  printf FMT ARGS       Formatted string
  indent N / nindent N  Indent / newline+indent

TYPE CONVERSION:
  toYaml               Convert to YAML string
  toJson               Convert to JSON string
  toString / atoi      String ↔ Integer
  b64enc / b64dec      Base64 encode/decode
  sha256sum            SHA256 hash

DEFAULTS:
  default VALUE        Use VALUE if empty/nil
  required "msg"       Fail with msg if empty
  empty                Check if empty

LIST:
  list "a" "b"         Create list
  first / last         First/last element
  has "x" LIST         Contains check
  join "," LIST        Join with separator
  uniq / without       Deduplicate / remove items
  append / prepend     Add to list

DICT:
  dict "k1" "v1"      Create dict
  get DICT "key"       Get value
  set DICT "key" "val" Set value
  hasKey DICT "key"    Key exists check
  keys / values        Get keys/values
  merge D1 D2          Merge dicts
  deepCopy             Deep copy
```

---

## 📊 Values Priority (Override Order)

```
LOWEST ─────────────────────────────────────────→ HIGHEST

Chart defaults  <  Parent chart  <  -f file(s)  <  --set
(values.yaml)     (if subchart)     (in order)     (wins!)

Multiple -f files: later files override earlier ones
Multiple --set:    later flags override earlier ones
```

---

## 🪝 Hooks Reference

```
HOOK TYPE         WHEN IT RUNS
─────────         ──────────────────────────────────
pre-install       Before resources created (install)
post-install      After resources loaded (install)
pre-upgrade       Before resources updated (upgrade)
post-upgrade      After resources updated (upgrade)
pre-delete        Before resources deleted
post-delete       After resources deleted
pre-rollback      Before rollback
post-rollback     After rollback
test              When 'helm test' runs

ANNOTATIONS:
  "helm.sh/hook": pre-install           ← Hook type(s)
  "helm.sh/hook-weight": "-5"           ← Order (lower=first)
  "helm.sh/hook-delete-policy":         ← Cleanup:
      before-hook-creation                 Delete old before new
      hook-succeeded                       Delete after success
      hook-failed                          Delete after failure
```

---

## ⚡ Useful Flag Combos

```bash
# Safe production deploy (auto-rollback on failure)
helm upgrade --install <release> <chart> \
  -f values-prod.yaml \
  --namespace production \
  --create-namespace \
  --atomic \
  --wait \
  --timeout 10m \
  --history-max 10

# Dry run (preview, no deploy)
helm install <release> <chart> --dry-run --debug

# Template render (no cluster needed)
helm template <release> <chart> -f values.yaml

# Show diff before upgrade (needs helm-diff plugin)
helm diff upgrade <release> <chart> -f values.yaml

# Force string type (prevent "1.0" → 1)
helm install <release> <chart> --set-string image.tag=1.0

# Reset to chart defaults on upgrade
helm upgrade <release> <chart> --reset-values -f values.yaml
```

---

## 📦 Chart.yaml Quick Reference

```yaml
apiVersion: v2                     # Always v2 for Helm 3
name: my-chart                     # Chart name
description: A great chart         # Description
type: application                  # application or library
version: 1.2.3                     # Chart version (SemVer)
appVersion: "4.5.6"               # App version (string)
kubeVersion: ">=1.24.0-0"         # Min K8s version
deprecated: false                  # Deprecation flag

dependencies:
  - name: postgresql               # Dependency chart name
    version: "12.x.x"             # Version range
    repository: "https://..."      # Or oci:// or file://
    condition: postgresql.enabled  # Toggle via values
    alias: db                      # Rename in this chart
    tags:                          # Group toggle
      - database
```

---

## 🔐 Security Checklist

```
✅ Never commit secrets in values.yaml / Git
✅ Use existingSecret pattern or External Secrets Operator
✅ Pin chart dependency versions (not "*" or latest)
✅ Set pod security contexts (runAsNonRoot, readOnly)
✅ Use --atomic for safe rollback on failure
✅ Limit history (--history-max 10)
✅ Use specific image tags (never :latest in prod)
✅ Add values.schema.json for input validation
✅ Scan charts (checkov, kube-score, Polaris)
✅ Use RBAC — don't run Helm as cluster-admin in CI
```

---

## 🔄 Common Workflows

### Deploy to Multiple Environments
```bash
# Same chart, different values per environment
helm upgrade --install my-app ./chart -f values-dev.yaml -n dev
helm upgrade --install my-app ./chart -f values-staging.yaml -n staging
helm upgrade --install my-app ./chart -f values-prod.yaml -n production
```

### CI/CD Pipeline Pattern
```bash
# 1. Lint
helm lint ./chart -f values-prod.yaml

# 2. Render & validate
helm template test ./chart -f values-prod.yaml | kubeval -

# 3. Package
helm package ./chart

# 4. Push to OCI
helm push chart-1.0.0.tgz oci://registry.example.com/charts

# 5. Deploy
helm upgrade --install my-app oci://registry.example.com/charts/chart \
  --version 1.0.0 -f values-prod.yaml --atomic --wait
```

### Rollback After Bad Deploy
```bash
helm history my-app              # Find good revision
helm rollback my-app <revision>  # Rollback
helm history my-app              # Verify new revision created
```

---

## 🛠️ Useful Plugins

```
helm-diff        Preview changes before upgrade
helm-secrets     Encrypted values (SOPS)
helmfile         Declarative multi-release management
helm-docs        Auto-generate docs from values
chart-testing    CI lint & test tool
```

---

## 🎓 Quick Debug Flow

```
Problem?
  │
  ├── Template error? ───→ helm lint ./chart
  │                        helm template rel ./chart --debug
  │
  ├── Wrong values? ─────→ helm get values <release> --all
  │                        helm template rel ./chart -f vals.yaml
  │
  ├── Deploy failed? ────→ helm status <release>
  │                        helm history <release>
  │                        kubectl describe pod <pod-name>
  │                        kubectl logs <pod-name>
  │
  └── Need rollback? ────→ helm history <release>
                           helm rollback <release> <revision>
```

---

> 📖 **Full Guide**: [Back to README](../README.md)
> 🛠️ **Examples**: [Practice Examples](../examples/)
