# Chapter 10: Advanced Patterns & Best Practices 🏆

## 🔴 ADVANCED LEVEL

---

## 🏗️ Pattern 1: Umbrella Charts (Multi-Service)

```
╔══════════════════════════════════════════════════════════════════════╗
║                    UMBRELLA CHART PATTERN                            ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Problem: You have 10 microservices that deploy together            ║
║  Solution: One "umbrella" chart that wraps them all                 ║
║                                                                      ║
║  📦 my-platform/           ← Umbrella chart                        ║
║  ├── Chart.yaml                                                      ║
║  │   dependencies:                                                   ║
║  │     - name: frontend          (subchart)                         ║
║  │     - name: api-gateway       (subchart)                         ║
║  │     - name: user-service      (subchart)                         ║
║  │     - name: order-service     (subchart)                         ║
║  │     - name: postgresql        (external chart)                   ║
║  │     - name: redis             (external chart)                   ║
║  │     - name: rabbitmq          (external chart)                   ║
║  │                                                                   ║
║  ├── values.yaml           ← Configure ALL services here           ║
║  ├── values-dev.yaml                                                ║
║  ├── values-prod.yaml                                               ║
║  ├── templates/            ← Shared resources (namespace, etc.)     ║
║  └── charts/               ← All sub-charts here                   ║
║                                                                      ║
║  ONE command deploys EVERYTHING:                                    ║
║  helm install my-platform ./my-platform -f values-prod.yaml        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

```yaml
# Umbrella Chart.yaml
apiVersion: v2
name: my-platform
version: 1.0.0
description: Complete platform deployment
type: application

dependencies:
  - name: frontend
    version: "1.x.x"
    repository: "file://../frontend-chart"   # Local chart
    condition: frontend.enabled

  - name: api-gateway
    version: "2.x.x"
    repository: "file://../api-gateway-chart"
    condition: api-gateway.enabled

  - name: user-service
    version: "1.x.x"
    repository: "oci://ghcr.io/myorg/charts/user-service"
    condition: user-service.enabled

  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled

  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

```yaml
# Umbrella values.yaml
global:
  imageRegistry: ghcr.io/myorg
  domain: example.com
  environment: production

frontend:
  enabled: true
  replicaCount: 3
  image:
    tag: "2.1.0"
  ingress:
    enabled: true
    host: "www.{{ .Values.global.domain }}"

api-gateway:
  enabled: true
  replicaCount: 2

user-service:
  enabled: true
  replicaCount: 3

postgresql:
  enabled: true
  auth:
    existingSecret: "platform-db-creds"

redis:
  enabled: true
```

---

## 🏗️ Pattern 2: Library Charts (Shared Code)

```
┌──────────────────────────────────────────────────────────────────┐
│                    LIBRARY CHART PATTERN                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Problem: 20 microservice charts all have the same boilerplate  │
│  Solution: Extract common templates into a library chart        │
│                                                                  │
│  📦 common-library/ (type: library)                             │
│  ├── Chart.yaml                                                  │
│  └── templates/                                                  │
│      └── _helpers.tpl      ← Shared template functions          │
│          ├── common.deployment                                   │
│          ├── common.service                                      │
│          ├── common.ingress                                      │
│          ├── common.labels                                       │
│          ├── common.configmap                                    │
│          └── common.hpa                                          │
│                                                                  │
│  Each service chart:                                             │
│  📦 user-service/                                               │
│  ├── Chart.yaml                                                  │
│  │   dependencies:                                               │
│  │     - name: common-library                                   │
│  ├── values.yaml                                                 │
│  └── templates/                                                  │
│      └── deployment.yaml                                         │
│          {{ include "common.deployment" . }}  ← Uses library!   │
│                                                                  │
│  20 services × (50 lines boilerplate) = 1000 lines saved!      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Library Chart Example:

```yaml
# common-library/Chart.yaml
apiVersion: v2
name: common-library
version: 1.0.0
type: library            # ← Cannot be installed directly!
```

```yaml
# common-library/templates/_deployment.tpl
{{- define "common.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "common.fullname" . }}
  labels:
    {{- include "common.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount | default 1 }}
  selector:
    matchLabels:
      {{- include "common.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "common.selectorLabels" . | nindent 8 }}
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy | default "IfNotPresent" }}
          ports:
            - name: http
              containerPort: {{ .Values.containerPort | default 8080 }}
          {{- with .Values.resources }}
          resources:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.livenessProbe }}
          livenessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.readinessProbe }}
          readinessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
{{- end }}
```

### Using the Library:

```yaml
# user-service/Chart.yaml
apiVersion: v2
name: user-service
version: 1.0.0
dependencies:
  - name: common-library
    version: "1.x.x"
    repository: "oci://ghcr.io/myorg/charts/common-library"
```

```yaml
# user-service/templates/deployment.yaml
{{ include "common.deployment" . }}
```

---

## 🏗️ Pattern 3: Helmfile (Multi-Release Manager)

```
┌──────────────────────────────────────────────────────────────────┐
│                      HELMFILE                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Problem: You need to install 15 different Helm releases        │
│           in order, with different configs per environment       │
│  Solution: Helmfile — declarative spec for multiple releases    │
│                                                                  │
│  One helmfile.yaml → manages ALL your releases!                 │
│                                                                  │
│  helmfile sync   → Install/upgrade everything                   │
│  helmfile diff   → Preview changes                              │
│  helmfile destroy→ Remove everything                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```yaml
# helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami
  - name: prometheus
    url: https://prometheus-community.github.io/helm-charts
  - name: grafana
    url: https://grafana.github.io/helm-charts

environments:
  dev:
    values:
      - environments/dev/values.yaml
  staging:
    values:
      - environments/staging/values.yaml
  production:
    values:
      - environments/production/values.yaml

releases:
  # Infrastructure
  - name: ingress-nginx
    namespace: ingress-nginx
    chart: ingress-nginx/ingress-nginx
    version: 4.8.0
    values:
      - values/ingress.yaml

  # Monitoring
  - name: prometheus
    namespace: monitoring
    chart: prometheus/kube-prometheus-stack
    version: 55.0.0
    values:
      - values/prometheus.yaml

  - name: grafana
    namespace: monitoring
    chart: grafana/grafana
    version: 7.0.0
    needs:            # Dependency ordering!
      - monitoring/prometheus
    values:
      - values/grafana.yaml

  # Application
  - name: my-api
    namespace: {{ .Environment.Name }}
    chart: ./charts/my-api
    values:
      - values/my-api.yaml
      - values/my-api.{{ .Environment.Name }}.yaml
    set:
      - name: image.tag
        value: {{ requiredEnv "IMAGE_TAG" }}

  - name: my-frontend
    namespace: {{ .Environment.Name }}
    chart: ./charts/my-frontend
    needs:
      - {{ .Environment.Name }}/my-api
    values:
      - values/my-frontend.yaml
```

```bash
# Deploy everything to dev
helmfile -e dev sync

# Preview changes for production
helmfile -e production diff

# Deploy specific release
helmfile -e production -l name=my-api sync

# Destroy everything
helmfile -e dev destroy
```

---

## 🔒 Security Best Practices

```
╔══════════════════════════════════════════════════════════════════════╗
║                    HELM SECURITY CHECKLIST                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. ✅ NEVER commit secrets in values.yaml                          ║
║     Use: existingSecret, external-secrets, helm-secrets plugin      ║
║                                                                      ║
║  2. ✅ Pin chart versions in dependencies                           ║
║     Bad:  version: "*"                                              ║
║     Good: version: "12.1.2"                                        ║
║                                                                      ║
║  3. ✅ Use values.schema.json for input validation                  ║
║     Prevent misconfigurations before they reach the cluster         ║
║                                                                      ║
║  4. ✅ Set security contexts in templates                           ║
║     securityContext:                                                 ║
║       runAsNonRoot: true                                            ║
║       readOnlyRootFilesystem: true                                  ║
║       allowPrivilegeEscalation: false                               ║
║       capabilities:                                                  ║
║         drop: [ALL]                                                  ║
║                                                                      ║
║  5. ✅ Verify chart provenance (signatures)                         ║
║     helm verify my-chart-1.0.0.tgz                                 ║
║     helm install --verify ...                                       ║
║                                                                      ║
║  6. ✅ Use --atomic for safe rollbacks                              ║
║     Automatically rolls back failed deployments                     ║
║                                                                      ║
║  7. ✅ Limit history revisions                                      ║
║     --history-max 10                                                ║
║     Prevents secret accumulation (releases stored as secrets)       ║
║                                                                      ║
║  8. ✅ RBAC: Give Helm only needed permissions                      ║
║     Don't run Helm as cluster-admin in CI/CD                       ║
║                                                                      ║
║  9. ✅ Scan charts for vulnerabilities                              ║
║     Tools: checkov, kubesec, kube-score, Polaris                   ║
║                                                                      ║
║  10. ✅ Use specific image tags (never :latest in prod)             ║
║      image:                                                          ║
║        tag: "1.27.0"    ← Good                                     ║
║        tag: "latest"    ← Bad (unpredictable!)                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 🔄 CI/CD Integration Patterns

### Pattern: GitOps with Helm

```
┌──────────────────────────────────────────────────────────────────┐
│                    GITOPS WITH HELM                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Option A: ArgoCD + Helm                                         │
│  ──────────────────────────                                      │
│                                                                  │
│  1. Git repo has chart + values                                  │
│  2. ArgoCD watches the repo                                      │
│  3. Change pushed → ArgoCD auto-syncs                            │
│                                                                  │
│  ┌──────┐    push     ┌──────┐    watch    ┌──────────┐        │
│  │ Dev  │────────────→│ Git  │◄────────────│ ArgoCD   │        │
│  └──────┘             └──────┘             │          │        │
│                                            │  sync    │        │
│                                            └────┬─────┘        │
│                                                 │              │
│                                                 ▼              │
│                                          ┌──────────┐          │
│                                          │ K8s      │          │
│                                          │ Cluster  │          │
│                                          └──────────┘          │
│                                                                  │
│  Option B: FluxCD + Helm                                         │
│  ──────────────────────                                          │
│                                                                  │
│  HelmRelease CRD in Git:                                        │
│  apiVersion: helm.toolkit.fluxcd.io/v2beta1                    │
│  kind: HelmRelease                                               │
│  metadata:                                                       │
│    name: my-app                                                  │
│  spec:                                                           │
│    chart:                                                        │
│      spec:                                                       │
│        chart: my-app                                             │
│        sourceRef:                                                │
│          kind: HelmRepository                                    │
│          name: my-repo                                           │
│    values:                                                       │
│      replicaCount: 5                                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Pattern: CI/CD Pipeline

```yaml
# Generic CI/CD Pipeline Pattern
# (GitHub Actions / GitLab CI / Jenkins)

# ═══════════════════════════════════════════════════════
# stages: lint → test → package → deploy
# ═══════════════════════════════════════════════════════

# Stage 1: LINT
# helm lint ./chart -f values-prod.yaml
# helm template test ./chart -f values-prod.yaml | kubeval -

# Stage 2: TEST (on temp namespace)
# helm upgrade --install test-release ./chart \
#   --namespace test-${CI_PIPELINE_ID} \
#   --create-namespace \
#   --wait --timeout 5m \
#   --set image.tag=${IMAGE_TAG}
# helm test test-release -n test-${CI_PIPELINE_ID}
# helm uninstall test-release -n test-${CI_PIPELINE_ID}

# Stage 3: PACKAGE
# helm package ./chart --version ${CHART_VERSION}
# helm push chart-${CHART_VERSION}.tgz oci://registry/charts

# Stage 4: DEPLOY
# helm upgrade --install my-app oci://registry/charts/my-app \
#   --version ${CHART_VERSION} \
#   --namespace production \
#   -f values-prod.yaml \
#   --set image.tag=${IMAGE_TAG} \
#   --wait --atomic --timeout 10m \
#   --history-max 10
```

---

## 📐 Chart Design Best Practices

```
┌──────────────────────────────────────────────────────────────────┐
│              CHART DESIGN BEST PRACTICES                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📝 NAMING                                                       │
│  ├── Chart names: lowercase, hyphenated (my-awesome-app)        │
│  ├── Template names: chartname.resource (my-app.deployment)     │
│  ├── Values: camelCase (replicaCount, not replica_count)        │
│  └── K8s names: truncate to 63 chars (K8s DNS limit)            │
│                                                                  │
│  📊 VALUES                                                       │
│  ├── Use flat structure where possible                           │
│  ├── Always provide sensible defaults                            │
│  ├── Use 'enabled' booleans for optional features               │
│  ├── Document every value with comments                         │
│  ├── Support 'existingSecret' pattern                           │
│  └── Add values.schema.json for validation                      │
│                                                                  │
│  📄 TEMPLATES                                                    │
│  ├── Use _helpers.tpl for all reusable snippets                │
│  ├── Always use 'include' over 'template'                       │
│  ├── Use nindent for proper YAML indentation                    │
│  ├── Handle nil values with 'default'                           │
│  ├── Add NOTES.txt with useful post-install info               │
│  └── Include health checks (liveness/readiness probes)          │
│                                                                  │
│  📦 VERSIONING                                                   │
│  ├── Follow SemVer strictly                                      │
│  ├── Bump chart version for ANY change                          │
│  ├── Bump major for breaking value changes                      │
│  ├── Keep appVersion in sync with actual app                    │
│  └── Use Chart.lock for reproducible builds                     │
│                                                                  │
│  🧪 TESTING                                                      │
│  ├── Always include at least one helm test                      │
│  ├── Lint in CI (helm lint)                                     │
│  ├── Template render in CI (helm template)                      │
│  ├── Use ct (chart-testing) tool for PRs                       │
│  └── Test with multiple values files                            │
│                                                                  │
│  📖 DOCUMENTATION                                                │
│  ├── Write clear README.md                                       │
│  ├── Document all values (use helm-docs tool!)                  │
│  ├── Include examples for common configurations                  │
│  └── Document breaking changes in CHANGELOG                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Essential Helm Plugins & Tools

```
┌──────────────────────┬──────────────────────────────────────────┐
│ Tool                 │ Purpose                                  │
├──────────────────────┼──────────────────────────────────────────┤
│ helm-diff            │ Preview changes before upgrade           │
│                      │ helm diff upgrade my-app ./chart         │
├──────────────────────┼──────────────────────────────────────────┤
│ helm-secrets         │ Encrypted values files (SOPS)            │
│                      │ helm secrets install ... -f enc.yaml     │
├──────────────────────┼──────────────────────────────────────────┤
│ helmfile             │ Declarative multi-release management     │
│                      │ helmfile sync                            │
├──────────────────────┼──────────────────────────────────────────┤
│ helm-docs            │ Auto-generate docs from values.yaml      │
│                      │ helm-docs --chart-search-root ./charts   │
├──────────────────────┼──────────────────────────────────────────┤
│ chart-testing (ct)   │ Lint & test charts in CI                 │
│                      │ ct lint --all                            │
├──────────────────────┼──────────────────────────────────────────┤
│ kubeval              │ Validate rendered YAML against K8s spec  │
│                      │ helm template ... | kubeval -            │
├──────────────────────┼──────────────────────────────────────────┤
│ kube-score           │ Score K8s manifests for best practices   │
│                      │ helm template ... | kube-score score -   │
├──────────────────────┼──────────────────────────────────────────┤
│ Polaris              │ Best practices checks                    │
│                      │ polaris audit --helm-chart ./my-chart    │
├──────────────────────┼──────────────────────────────────────────┤
│ chart-releaser (cr)  │ GitHub Action for chart publishing       │
│                      │ Automates GitHub Pages chart repo        │
├──────────────────────┼──────────────────────────────────────────┤
│ nova                 │ Find outdated Helm releases              │
│                      │ nova find --wide                         │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## 🧠 Knowledge Check

```
Q1: What is an umbrella chart?
A:  A chart that has no templates of its own but
    depends on multiple sub-charts. Deploys an
    entire platform in one release.

Q2: What's a library chart used for?
A:  Sharing reusable template functions across charts.
    type: library in Chart.yaml. Can't be installed alone.

Q3: Name 3 security best practices for Helm.
A:  1. Never commit secrets in values.yaml
    2. Pin chart dependency versions
    3. Set pod security contexts (non-root, read-only fs)
    4. Use --atomic for safe rollbacks
    5. Scan charts with security tools

Q4: What is Helmfile?
A:  A declarative tool that manages multiple Helm
    releases, with environment-specific values and
    dependency ordering.

Q5: How does GitOps work with Helm?
A:  Tools like ArgoCD/FluxCD watch a Git repo for
    chart/values changes and auto-sync to the cluster.
```

---

## 🏆 Congratulations! You've completed the Helm Mastery Guide!

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🏆 YOU ARE NOW A HELM EXPERT! 🏆                              ║
║                                                                  ║
║   You've learned:                                                ║
║   ✅ What Helm is and why it exists                              ║
║   ✅ Helm architecture (client-only, no Tiller)                  ║
║   ✅ Installing and using Helm                                   ║
║   ✅ Chart structure (every file explained)                      ║
║   ✅ Go templating (functions, conditionals, loops)              ║
║   ✅ Values system (multi-env, priority, secrets)                ║
║   ✅ Every Helm command                                          ║
║   ✅ Hooks and lifecycle management                              ║
║   ✅ Chart repositories (classic + OCI)                          ║
║   ✅ Advanced patterns (umbrella, library, Helmfile)             ║
║   ✅ Security and CI/CD best practices                           ║
║                                                                  ║
║   Go build amazing charts! 🚀                                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

**← [Back to Index](../README.md)**
**📋 [Cheat Sheet](../cheatsheets/helm-cheatsheet.md)**
**🛠️ [Practice Examples](../examples/)**
