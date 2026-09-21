# Chapter 8: Hooks & Tests 🪝🧪

## 🔴 ADVANCED LEVEL

---

## 🪝 What Are Helm Hooks?

```
╔══════════════════════════════════════════════════════════════════════╗
║                        HELM HOOKS                                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Hooks = Kubernetes resources that run at SPECIFIC POINTS            ║
║          during a release lifecycle.                                 ║
║                                                                      ║
║  Think of them as "event listeners" for your release:               ║
║                                                                      ║
║  "Before installing, run database migration"                        ║
║  "After upgrading, send a Slack notification"                       ║
║  "Before deleting, backup the database"                             ║
║                                                                      ║
║  Hooks are regular K8s resources (usually Jobs or Pods)             ║
║  with special annotations.                                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Hook Types (Lifecycle Events)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    RELEASE LIFECYCLE & HOOKS                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  helm install my-app ./chart                                        │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────────────┐                                            │
│  │  pre-install        │ ← Hook runs BEFORE resources created       │
│  │  (e.g., db migrate) │                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  Install resources  │ ← Normal K8s resources created             │
│  │  (deployment, svc)  │                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  post-install       │ ← Hook runs AFTER resources created        │
│  │  (e.g., load data)  │                                            │
│  └─────────────────────┘                                            │
│                                                                      │
│                                                                      │
│  helm upgrade my-app ./chart                                        │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────────────┐                                            │
│  │  pre-upgrade        │ ← Hook runs BEFORE upgrade                 │
│  │  (e.g., backup db)  │                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  Upgrade resources  │ ← Resources updated                        │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  post-upgrade       │ ← Hook runs AFTER upgrade                  │
│  │  (e.g., clear cache)│                                            │
│  └─────────────────────┘                                            │
│                                                                      │
│                                                                      │
│  helm uninstall my-app                                              │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────────────┐                                            │
│  │  pre-delete         │ ← Hook runs BEFORE deletion                │
│  │  (e.g., final backup│                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  Delete resources   │ ← Resources removed                        │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  post-delete        │ ← Hook runs AFTER deletion                 │
│  │  (e.g., cleanup)    │                                            │
│  └─────────────────────┘                                            │
│                                                                      │
│                                                                      │
│  helm rollback my-app 1                                             │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────────────┐                                            │
│  │  pre-rollback       │                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  Rollback resources │                                            │
│  └──────────┬──────────┘                                            │
│             ▼                                                        │
│  ┌─────────────────────┐                                            │
│  │  post-rollback      │                                            │
│  └─────────────────────┘                                            │
│                                                                      │
│                                                                      │
│  SPECIAL:                                                            │
│  ┌─────────────────────┐                                            │
│  │  test               │ ← Runs with: helm test my-app             │
│  │  (e.g., smoke test) │                                            │
│  └─────────────────────┘                                            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### All Hook Types:

```
┌─────────────────┬──────────────────────────────────────────────┐
│ Hook            │ When it runs                                 │
├─────────────────┼──────────────────────────────────────────────┤
│ pre-install     │ After templates rendered, before K8s create  │
│ post-install    │ After all resources loaded into K8s          │
│ pre-upgrade     │ After templates rendered, before K8s update  │
│ post-upgrade    │ After all resources updated in K8s           │
│ pre-delete      │ Before any resources deleted from K8s        │
│ post-delete     │ After all resources deleted from K8s         │
│ pre-rollback    │ After templates rendered, before rollback    │
│ post-rollback   │ After all resources rolled back              │
│ test            │ When 'helm test' is called                   │
└─────────────────┴──────────────────────────────────────────────┘
```

---

## 🔧 Creating Hooks

### Example 1: Database Migration (pre-install/pre-upgrade)

```yaml
# templates/hooks/db-migrate.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-chart.fullname" . }}-db-migrate
  labels:
    {{- include "my-chart.labels" . | nindent 4 }}
  annotations:
    # ════════════════════════════════════════════════
    # These annotations make it a HOOK
    # ════════════════════════════════════════════════
    "helm.sh/hook": pre-install,pre-upgrade
    #               ↑ Runs before install AND upgrade

    "helm.sh/hook-weight": "-5"
    #                       ↑ Lower weight = runs first
    #                         (useful for ordering multiple hooks)

    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
    #                              ↑ When to delete this Job
spec:
  template:
    metadata:
      name: {{ include "my-chart.fullname" . }}-db-migrate
    spec:
      restartPolicy: Never
      containers:
        - name: db-migrate
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
          command: ["python", "manage.py", "migrate"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "my-chart.fullname" . }}-db
                  key: url
  backoffLimit: 3
```

### Example 2: Post-Install Data Loading

```yaml
# templates/hooks/load-data.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-chart.fullname" . }}-load-data
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: load-data
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
          command: ["python", "manage.py", "loaddata", "initial_data.json"]
  backoffLimit: 1
```

### Example 3: Pre-Delete Backup

```yaml
# templates/hooks/backup.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-chart.fullname" . }}-backup
  annotations:
    "helm.sh/hook": pre-delete
    "helm.sh/hook-weight": "-10"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: backup
          image: postgres:15
          command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL > /backup/dump-$(date +%Y%m%d).sql
              aws s3 cp /backup/ s3://my-backups/ --recursive
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
          volumeMounts:
            - name: backup-volume
              mountPath: /backup
      volumes:
        - name: backup-volume
          emptyDir: {}
  backoffLimit: 2
```

---

## 📊 Hook Annotations Explained

### hook-weight (Execution Order)

```
┌──────────────────────────────────────────────────────────────────┐
│                    HOOK WEIGHT ORDER                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Multiple pre-install hooks? They run in WEIGHT ORDER:          │
│                                                                  │
│  Weight: -10        -5          0           5          10        │
│           │          │          │           │           │        │
│           ▼          ▼          ▼           ▼           ▼        │
│        ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐      │
│        │Create│  │ DB   │  │ Load │  │ Warm │  │Notify│      │
│        │Schema│  │Migrate│  │Config│  │Cache │  │Slack │      │
│        └──────┘  └──────┘  └──────┘  └──────┘  └──────┘      │
│        FIRST ────────────────────────────────────→ LAST        │
│                                                                  │
│  Same weight? Sorted by resource kind, then name (alphabetical)│
│                                                                  │
│  Default weight: 0                                              │
│  Range: any integer (negative values run first)                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### hook-delete-policy (Cleanup)

```
┌──────────────────────┬───────────────────────────────────────────┐
│ Delete Policy        │ Behavior                                  │
├──────────────────────┼───────────────────────────────────────────┤
│                      │                                           │
│ before-hook-creation │ Delete previous hook resource BEFORE      │
│                      │ launching new hook (on next install/      │
│                      │ upgrade). Good for cleaning up old Jobs.  │
│                      │                                           │
│ hook-succeeded       │ Delete hook resource AFTER it succeeds.   │
│                      │ Keeps things clean. Most common.          │
│                      │                                           │
│ hook-failed          │ Delete hook resource if it FAILS.         │
│                      │ Useful if you don't need failed Job logs. │
│                      │                                           │
└──────────────────────┴───────────────────────────────────────────┘

Common combinations:
━━━━━━━━━━━━━━━━━━━━

  # Clean up on success, keep on failure (for debugging):
  "helm.sh/hook-delete-policy": hook-succeeded

  # Always clean up (success or failure):
  "helm.sh/hook-delete-policy": hook-succeeded,hook-failed

  # Clean up old runs when new hook starts:
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

---

## ⚠️ Important Hook Behaviors

```
┌──────────────────────────────────────────────────────────────────┐
│                 HOOK GOTCHAS & RULES                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Hooks are NOT managed as part of the release               │
│     • helm uninstall does NOT delete hook resources             │
│     • Use hook-delete-policy for cleanup                       │
│     • hook resources won't appear in helm get manifest          │
│                                                                  │
│  2. Hooks BLOCK the release process                             │
│     • Helm waits for hook to complete (reach Ready state)       │
│     • If hook fails → release fails                            │
│     • Use --timeout to prevent infinite waiting                 │
│                                                                  │
│  3. If hook resource already exists → ERROR                     │
│     • Use "before-hook-creation" delete policy                 │
│     • Or use unique names with revision:                       │
│       name: {{ .Release.Name }}-migrate-{{ .Release.Revision }}│
│                                                                  │
│  4. Hooks can fire on MULTIPLE events                          │
│     • "helm.sh/hook": pre-install,pre-upgrade                 │
│     • Same resource, triggered by both events                  │
│                                                                  │
│  5. Hook resources aren't tracked for rollback                 │
│     • Rolling back doesn't re-run pre-install hooks            │
│     • pre-rollback hooks run instead                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Helm Tests

### What Are Helm Tests?

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  Helm Tests = Pods that verify your release works correctly     ║
║                                                                  ║
║  Run with:  helm test <release-name>                            ║
║                                                                  ║
║  They are hooks with: "helm.sh/hook": test                      ║
║                                                                  ║
║  Common test types:                                              ║
║  • Connection test (can I reach the service?)                   ║
║  • API health check (is /healthz returning 200?)                ║
║  • Data validation (is initial data loaded?)                    ║
║  • Integration test (can the app talk to the DB?)               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Example Tests:

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-chart.fullname" . }}-test-connection"
  labels:
    {{- include "my-chart.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "my-chart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

```yaml
# templates/tests/test-api-health.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-chart.fullname" . }}-test-health"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-weight": "1"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  containers:
    - name: curl
      image: curlimages/curl:latest
      command:
        - /bin/sh
        - -c
        - |
          echo "Testing health endpoint..."
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
            http://{{ include "my-chart.fullname" . }}:{{ .Values.service.port }}/healthz)
          
          if [ "$STATUS" = "200" ]; then
            echo "✅ Health check passed (HTTP $STATUS)"
            exit 0
          else
            echo "❌ Health check failed (HTTP $STATUS)"
            exit 1
          fi
  restartPolicy: Never
```

```yaml
# templates/tests/test-db-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-chart.fullname" . }}-test-db"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-weight": "2"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  containers:
    - name: pg-test
      image: postgres:15
      command:
        - /bin/sh
        - -c
        - |
          echo "Testing database connection..."
          pg_isready -h {{ .Values.postgresql.host }} \
                     -p {{ .Values.postgresql.port }} \
                     -U {{ .Values.postgresql.user }}
          
          if [ $? -eq 0 ]; then
            echo "✅ Database connection successful"
            exit 0
          else
            echo "❌ Database connection failed"
            exit 1
          fi
  restartPolicy: Never
```

### Running Tests:

```bash
# Run all tests
helm test my-app

# Run with timeout
helm test my-app --timeout 5m

# Show test pod logs
helm test my-app --logs

# Output:
# NAME: my-app
# LAST DEPLOYED: Mon Sep 21 2026
# NAMESPACE: default
# STATUS: deployed
# TEST SUITE:
#   my-app-test-connection  - Phase: Succeeded
#   my-app-test-health      - Phase: Succeeded
#   my-app-test-db          - Phase: Succeeded
```

```
Test execution flow:
━━━━━━━━━━━━━━━━━━━

  helm test my-app
       │
       ├── Creates test Pod 1 (weight: 0)
       │   └── Runs → ✅ Succeeded
       │
       ├── Creates test Pod 2 (weight: 1)
       │   └── Runs → ✅ Succeeded
       │
       └── Creates test Pod 3 (weight: 2)
           └── Runs → ✅ Succeeded

  All tests passed! 🎉

  If any test fails:
       │
       ├── Test Pod 2 → ❌ Failed
       │
       └── helm test reports FAILURE
           (remaining tests may still run)
```

---

## 🧠 Knowledge Check

```
Q1: What annotation makes a resource a hook?
A:  "helm.sh/hook": <event-type>
    e.g., "helm.sh/hook": pre-install

Q2: How do you control the order of multiple hooks?
A:  "helm.sh/hook-weight": "<number>"
    Lower numbers run first. Default is 0.

Q3: Why use hook-delete-policy?
A:  Hook resources aren't managed by the release.
    Without cleanup, old Jobs/Pods pile up.

Q4: What's a Helm test?
A:  A Pod with annotation "helm.sh/hook": test
    Run with: helm test <release>
    Exit 0 = pass, non-zero = fail

Q5: Do hooks run during rollback?
A:  Only pre-rollback and post-rollback hooks run.
    pre-install/pre-upgrade hooks do NOT re-run.
```

---

**Next → [Chapter 9: Chart Repositories](09-repositories.md)** ➡️
