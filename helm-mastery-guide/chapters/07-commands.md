# Chapter 7: Helm Commands Mastery 💪

## 🟡 INTERMEDIATE LEVEL

---

## 📋 Complete Command Map

```
╔══════════════════════════════════════════════════════════════════════╗
║                    HELM COMMAND CATEGORIES                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📦 RELEASE MANAGEMENT        📂 REPOSITORY MANAGEMENT              ║
║  ├── helm install              ├── helm repo add                    ║
║  ├── helm upgrade              ├── helm repo list                   ║
║  ├── helm rollback             ├── helm repo remove                 ║
║  ├── helm uninstall            ├── helm repo update                 ║
║  ├── helm list                 └── helm repo index                  ║
║  ├── helm status                                                     ║
║  ├── helm history             🔍 SEARCH & DISCOVERY                 ║
║  └── helm get                  ├── helm search repo                 ║
║                                ├── helm search hub                  ║
║  🏗️ CHART DEVELOPMENT          └── helm show (chart/values/all)     ║
║  ├── helm create                                                     ║
║  ├── helm template            🔌 PLUGIN MANAGEMENT                  ║
║  ├── helm lint                 ├── helm plugin install               ║
║  ├── helm package              ├── helm plugin list                  ║
║  ├── helm dependency           ├── helm plugin uninstall             ║
║  └── helm test                 └── helm plugin update                ║
║                                                                      ║
║  🔧 ENVIRONMENT                ⬇️ CHART DISTRIBUTION                ║
║  ├── helm env                  ├── helm pull                        ║
║  ├── helm version              ├── helm push (OCI)                  ║
║  └── helm completion           └── helm registry                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 📦 Release Management Commands

### `helm install` — Deploy a chart

```bash
# ═══════════════════════════════════════════════════════
# BASIC SYNTAX
# ═══════════════════════════════════════════════════════
helm install [RELEASE_NAME] [CHART] [flags]

# ─── From repository ───
helm install my-nginx bitnami/nginx

# ─── From local directory ───
helm install my-app ./my-chart

# ─── From .tgz file ───
helm install my-app my-chart-1.2.3.tgz

# ─── From URL ───
helm install my-app https://example.com/charts/my-chart-1.2.3.tgz

# ─── From OCI registry ───
helm install my-app oci://registry.example.com/charts/my-chart --version 1.2.3

# ═══════════════════════════════════════════════════════
# USEFUL FLAGS
# ═══════════════════════════════════════════════════════
helm install my-app ./chart \
  --namespace production \          # Target namespace
  --create-namespace \              # Create ns if not exists
  -f values-prod.yaml \            # Values file
  --set replicaCount=5 \           # Override single value
  --set-string version="1.0" \     # Force string type
  --version 2.0.0 \                # Specific chart version
  --wait \                         # Wait for readiness
  --timeout 10m \                  # Timeout for --wait
  --atomic \                       # Rollback on failure
  --dry-run \                      # Preview without deploying
  --debug \                        # Verbose output
  --description "Initial deploy"   # Custom description

# ═══════════════════════════════════════════════════════
# UPGRADE OR INSTALL (install if not exists)
# ═══════════════════════════════════════════════════════
helm upgrade --install my-app ./chart   # ← Very common in CI/CD!
```

```
--atomic flag explained:
━━━━━━━━━━━━━━━━━━━━━━━

  WITHOUT --atomic:                 WITH --atomic:
  
  Install starts                    Install starts
       │                                 │
       ▼                                 ▼
  Pod crashes ❌                    Pod crashes ❌
       │                                 │
       ▼                                 ▼
  Release status: FAILED            Auto-rollback! ⏪
  Broken resources remain           Clean state restored
  Manual cleanup needed :(          No mess! :)
```

### `helm upgrade` — Update a release

```bash
# ═══════════════════════════════════════════════════════
# BASIC UPGRADE
# ═══════════════════════════════════════════════════════
helm upgrade my-app ./chart

# ═══════════════════════════════════════════════════════
# IMPORTANT FLAGS
# ═══════════════════════════════════════════════════════
helm upgrade my-app ./chart \
  -f values-prod.yaml \            # New values
  --set image.tag=v2.0 \           # Override
  --reuse-values \                 # Keep previous values (careful!)
  --reset-values \                 # Reset to chart defaults
  --wait \                         # Wait for rollout
  --atomic \                       # Rollback on failure
  --force \                        # Force resource updates
  --cleanup-on-fail \              # Delete new resources on failure
  --history-max 10                 # Limit stored revisions
```

```
⚠️ --reuse-values vs --reset-values
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Scenario: You installed with --set replicaCount=5
  Now upgrading with new chart version...

  helm upgrade my-app ./chart
  → replicaCount = back to default (values.yaml)! 😱
    Previous --set values are LOST

  helm upgrade my-app ./chart --reuse-values
  → replicaCount = 5 ✅ (keeps previous values)
  → But NEW default values in chart might be missing!

  BEST PRACTICE:
  Always pass your values file explicitly:
  helm upgrade my-app ./chart -f values-prod.yaml
```

### `helm rollback` — Revert to previous revision

```bash
# ═══════════════════════════════════════════════════════
# ROLLBACK
# ═══════════════════════════════════════════════════════

# First, check history
helm history my-app

# REVISION  STATUS       CHART       DESCRIPTION
# 1         superseded   app-1.0.0   Install
# 2         superseded   app-1.1.0   Upgrade
# 3         deployed     app-1.2.0   Upgrade (current)

# Rollback to revision 2
helm rollback my-app 2

# Rollback to the PREVIOUS revision (shorthand)
helm rollback my-app

# With flags
helm rollback my-app 2 \
  --wait \                # Wait for rollback to complete
  --timeout 5m \          # Timeout
  --force                 # Force resource updates
```

### `helm uninstall` — Remove a release

```bash
# ═══════════════════════════════════════════════════════
# UNINSTALL
# ═══════════════════════════════════════════════════════
helm uninstall my-app

# Keep release history (can still see it)
helm uninstall my-app --keep-history

# Specify namespace
helm uninstall my-app -n production

# Dry run (preview)
helm uninstall my-app --dry-run

# Wait for deletion
helm uninstall my-app --wait --timeout 5m
```

### `helm list` — List releases

```bash
# ═══════════════════════════════════════════════════════
# LIST RELEASES
# ═══════════════════════════════════════════════════════
helm list                           # Current namespace
helm list --all-namespaces          # All namespaces
helm list -n production             # Specific namespace

# Filter by status
helm list --deployed                # Only deployed
helm list --failed                  # Only failed
helm list --pending                 # Only pending
helm list --uninstalled             # Only uninstalled (kept history)
helm list --all                     # All statuses

# Filter by name
helm list --filter 'nginx'          # Regex filter
helm list -q                        # Names only (quiet)

# Output format
helm list -o json                   # JSON output
helm list -o yaml                   # YAML output
helm list -o table                  # Table (default)

# Sort
helm list --date                    # Sort by date
helm list --reverse                 # Reverse order
```

### `helm status` — Get release status

```bash
helm status my-app
helm status my-app -n production
helm status my-app --revision 2     # Specific revision
helm status my-app -o json          # JSON format
```

### `helm history` — Release revision history

```bash
helm history my-app
helm history my-app --max 5         # Limit results
helm history my-app -o json         # JSON format
```

### `helm get` — Get release details

```bash
# ═══════════════════════════════════════════════════════
# GET EVERYTHING ABOUT A RELEASE
# ═══════════════════════════════════════════════════════

helm get all my-app                 # Everything!
helm get manifest my-app            # Rendered K8s YAML
helm get values my-app              # User-supplied values
helm get values my-app --all        # All values (including defaults)
helm get values my-app --revision 1 # Values from revision 1
helm get hooks my-app               # Hook manifests
helm get notes my-app               # NOTES.txt output
helm get metadata my-app            # Release metadata
```

---

## 🏗️ Development Commands

### `helm create` — Scaffold a new chart

```bash
helm create my-chart
# Creates a full chart with nginx defaults
```

### `helm template` — Render templates locally

```bash
# ═══════════════════════════════════════════════════════
# RENDER WITHOUT INSTALLING (no cluster needed!)
# ═══════════════════════════════════════════════════════
helm template my-app ./my-chart

# With values
helm template my-app ./my-chart -f prod-values.yaml

# Specific template only
helm template my-app ./my-chart -s templates/deployment.yaml

# With --set
helm template my-app ./my-chart --set replicaCount=5

# Include CRDs
helm template my-app ./my-chart --include-crds

# Validate against K8s API versions
helm template my-app ./my-chart --validate

# Set namespace (for template rendering)
helm template my-app ./my-chart --namespace production

# Output to file
helm template my-app ./my-chart > rendered.yaml
```

### `helm lint` — Check chart for issues

```bash
helm lint ./my-chart
helm lint ./my-chart -f values-prod.yaml
helm lint ./my-chart --strict          # Treat warnings as errors
helm lint ./my-chart --with-subcharts  # Also lint subcharts
```

```
Lint output examples:
━━━━━━━━━━━━━━━━━━━━━

  ==> Linting ./my-chart
  [INFO]  Chart.yaml: icon is recommended
  [WARNING] templates/ingress.yaml: Deployment spec has no replicas field
  [ERROR] templates/broken.yaml: parse error at line 10

  ✅ 0 errors → chart is valid
  ⚠️ warnings → chart works but could be better
  ❌ errors → chart won't install
```

### `helm package` — Package chart into .tgz

```bash
helm package ./my-chart
helm package ./my-chart --destination ./releases/
helm package ./my-chart --version 2.0.0
helm package ./my-chart --app-version 5.0.0
helm package ./my-chart --dependency-update    # Update deps first
```

### `helm dependency` — Manage dependencies

```bash
helm dependency update ./my-chart    # Download deps
helm dependency build ./my-chart     # Rebuild from lock
helm dependency list ./my-chart      # Show deps & status
```

### `helm test` — Run chart tests

```bash
helm test my-app
helm test my-app --timeout 5m
helm test my-app --logs              # Show test pod logs
```

---

## 📂 Repository Commands

```bash
# ═══════════════════════════════════════════════════════
# REPOSITORY MANAGEMENT
# ═══════════════════════════════════════════════════════

# Add repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# With authentication
helm repo add private https://charts.example.com \
  --username admin --password secret

# Update all repos (fetch latest index)
helm repo update

# List repos
helm repo list

# Remove a repo
helm repo remove bitnami

# Generate repo index (for hosting your own repo)
helm repo index ./my-repo-dir --url https://charts.example.com
```

---

## 🔍 Search Commands

```bash
# ═══════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════

# Search your added repos
helm search repo nginx
helm search repo nginx --versions        # Show ALL versions
helm search repo nginx --version ">=15"  # Version constraint
helm search repo ""                      # List ALL charts

# Search Artifact Hub (internet)
helm search hub wordpress
helm search hub --max-col-width 80       # Wider output
```

---

## 🔍 Show / Inspect Commands

```bash
# ═══════════════════════════════════════════════════════
# INSPECT CHARTS BEFORE INSTALLING
# ═══════════════════════════════════════════════════════
helm show chart bitnami/nginx      # Chart.yaml info
helm show values bitnami/nginx     # Default values
helm show readme bitnami/nginx     # README
helm show all bitnami/nginx        # Everything
helm show crds bitnami/nginx       # CRDs (if any)

# Works with local charts too
helm show values ./my-chart
```

---

## ⬇️ Pull & Push Commands

```bash
# ═══════════════════════════════════════════════════════
# PULL (download chart without installing)
# ═══════════════════════════════════════════════════════
helm pull bitnami/nginx                     # Download .tgz
helm pull bitnami/nginx --untar             # Download & extract
helm pull bitnami/nginx --version 15.0.0    # Specific version
helm pull bitnami/nginx -d ./downloads/     # Custom destination

# Pull from OCI
helm pull oci://registry.example.com/charts/my-chart --version 1.0.0

# ═══════════════════════════════════════════════════════
# PUSH (to OCI registry)
# ═══════════════════════════════════════════════════════
helm push my-chart-1.0.0.tgz oci://registry.example.com/charts

# ═══════════════════════════════════════════════════════
# REGISTRY (OCI login/logout)
# ═══════════════════════════════════════════════════════
helm registry login registry.example.com
helm registry logout registry.example.com
```

---

## 🔌 Plugin Commands

```bash
# ═══════════════════════════════════════════════════════
# POPULAR PLUGINS
# ═══════════════════════════════════════════════════════

# Helm Diff (see changes before upgrading)
helm plugin install https://github.com/databus23/helm-diff
helm diff upgrade my-app ./chart -f values.yaml

# Helm Secrets (encrypted values)
helm plugin install https://github.com/jkroepke/helm-secrets
helm secrets install my-app ./chart -f secrets.yaml.enc

# Helm S3 (S3 as chart repo)
helm plugin install https://github.com/hypnoglow/helm-s3

# List installed plugins
helm plugin list

# Update plugin
helm plugin update diff

# Remove plugin
helm plugin uninstall diff
```

---

## 📊 Command Quick-Reference

```
┌──────────────────────┬──────────────────────────────────────────┐
│ Task                 │ Command                                  │
├──────────────────────┼──────────────────────────────────────────┤
│ Deploy app           │ helm install my-app ./chart             │
│ Update app           │ helm upgrade my-app ./chart             │
│ Deploy or update     │ helm upgrade --install my-app ./chart   │
│ Rollback             │ helm rollback my-app [revision]         │
│ Delete app           │ helm uninstall my-app                   │
│ List releases        │ helm list -A                            │
│ Release details      │ helm status my-app                     │
│ Release history      │ helm history my-app                    │
│ Rendered YAML        │ helm get manifest my-app               │
│ Used values          │ helm get values my-app --all           │
├──────────────────────┼──────────────────────────────────────────┤
│ Create chart         │ helm create my-chart                   │
│ Render templates     │ helm template my-app ./chart           │
│ Check for errors     │ helm lint ./chart                      │
│ Package chart        │ helm package ./chart                   │
│ Fetch dependencies   │ helm dep up ./chart                    │
├──────────────────────┼──────────────────────────────────────────┤
│ Add repo             │ helm repo add name url                 │
│ Update repos         │ helm repo update                       │
│ Search repo          │ helm search repo keyword               │
│ Show chart values    │ helm show values repo/chart            │
│ Download chart       │ helm pull repo/chart --untar           │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## 🧠 Knowledge Check

```
Q1: What does 'helm upgrade --install' do?
A:  Installs the release if it doesn't exist,
    upgrades it if it does. Idempotent!

Q2: What's the difference between --dry-run and 'helm template'?
A:  --dry-run: Sends to K8s API for validation (needs cluster)
    helm template: Pure local rendering (no cluster needed)

Q3: How do you see what a release actually deployed?
A:  helm get manifest my-app

Q4: What does --atomic do?
A:  Automatically rolls back if install/upgrade fails.
    Leaves the release in a clean state.

Q5: How do you preview changes before upgrading?
A:  helm diff upgrade my-app ./chart (needs diff plugin)
    or: helm upgrade ... --dry-run --debug
```

---

**Next → [Chapter 8: Hooks & Tests](08-hooks-tests.md)** ➡️
