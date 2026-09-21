# Chapter 2: Helm Architecture & Core Concepts 🏗️

## 🟢 BEGINNER LEVEL

---

## 🔍 Helm 3 Architecture Overview

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        HELM 3 ARCHITECTURE                              ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║                                                                          ║
║   👨‍💻 YOU (Developer / DevOps)                                           ║
║     │                                                                    ║
║     │  helm install my-app ./my-chart                                    ║
║     │                                                                    ║
║     ▼                                                                    ║
║   ┌──────────────────────────────────┐                                   ║
║   │         HELM CLIENT              │  ← Runs on YOUR machine          ║
║   │         (helm CLI)               │                                   ║
║   │                                  │                                   ║
║   │  1. Reads Chart files            │                                   ║
║   │  2. Merges Values                │                                   ║
║   │  3. Renders Templates            │                                   ║
║   │  4. Validates YAML               │                                   ║
║   └──────────┬───────────────────────┘                                   ║
║              │                                                           ║
║              │  Sends rendered YAML manifests                            ║
║              │  via Kubernetes API                                       ║
║              ▼                                                           ║
║   ┌──────────────────────────────────┐                                   ║
║   │     KUBERNETES API SERVER        │  ← Your K8s cluster              ║
║   │                                  │                                   ║
║   │  Receives K8s resources:         │                                   ║
║   │  • Deployments                   │                                   ║
║   │  • Services                      │                                   ║
║   │  • ConfigMaps                    │                                   ║
║   │  • etc.                          │                                   ║
║   └──────────┬───────────────────────┘                                   ║
║              │                                                           ║
║              │  Stores release info as                                   ║
║              │  Kubernetes Secrets                                       ║
║              ▼                                                           ║
║   ┌──────────────────────────────────┐                                   ║
║   │     KUBERNETES SECRETS           │                                   ║
║   │     (Release Storage)            │                                   ║
║   │                                  │                                   ║
║   │  sh.helm.release.v1.my-app.v1   │  ← Release revision 1            ║
║   │  sh.helm.release.v1.my-app.v2   │  ← Release revision 2            ║
║   │  sh.helm.release.v1.my-app.v3   │  ← Release revision 3            ║
║   └──────────────────────────────────┘                                   ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 🔑 Key Insight: No Server Component!

```
HELM 2 (OLD - Don't use)              HELM 3 (CURRENT ✅)
━━━━━━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━━━━━

  Client ──→ Tiller ──→ K8s           Client ──→ K8s API
              (server)                        (direct!)
              
  ❌ Security risk                    ✅ No server needed
  ❌ Cluster admin access             ✅ Uses your kubeconfig
  ❌ Complex RBAC                     ✅ Native K8s RBAC
  ❌ Single point of failure          ✅ Stateless client

  Tiller was REMOVED in Helm 3! 🎉
```

---

## 🔄 The Helm Workflow: Step by Step

### What happens when you run `helm install`?

```
helm install my-web-app ./my-chart --values prod-values.yaml

Step 1: LOAD CHART
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📦 my-chart/
  ├── Chart.yaml          ← Chart metadata (name, version)
  ├── values.yaml         ← Default configuration
  ├── templates/          ← Kubernetes YAML templates
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   └── ingress.yaml
  └── charts/             ← Dependencies (sub-charts)

  Helm reads all these files into memory.


Step 2: MERGE VALUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────┐   ┌──────────────────┐   ┌───────────────┐
  │ Chart defaults │ + │ prod-values.yaml │ + │ --set flags   │
  │ (values.yaml)  │   │ (your overrides) │   │ (CLI args)    │
  └────────┬───────┘   └────────┬─────────┘   └───────┬───────┘
           │                    │                      │
           └────────────────────┼──────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   MERGED VALUES       │
                    │                       │
                    │  Priority (low→high): │
                    │  1. Chart defaults    │
                    │  2. Values file (-f)  │
                    │  3. --set flags       │
                    └───────────┬───────────┘
                                │
                                ▼

Step 3: RENDER TEMPLATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Template (before):                Rendered (after):
  ┌──────────────────────┐         ┌──────────────────────┐
  │ apiVersion: apps/v1  │         │ apiVersion: apps/v1  │
  │ kind: Deployment     │         │ kind: Deployment     │
  │ metadata:            │   ──→   │ metadata:            │
  │   name: {{ .Release  │         │   name: my-web-app   │
  │     .Name }}         │         │ spec:                │
  │ spec:                │         │   replicas: 5        │
  │   replicas: {{       │         │   image: myapp:2.1.0 │
  │     .Values          │         └──────────────────────┘
  │     .replicaCount }} │
  └──────────────────────┘


Step 4: VALIDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Is the YAML valid?
  ✅ Are the K8s resource definitions correct?
  ✅ Do the API versions exist in the cluster?


Step 5: SEND TO KUBERNETES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Rendered YAML ──→ Kubernetes API Server
                         │
                         ├── Creates Deployment
                         ├── Creates Service
                         ├── Creates Ingress
                         └── Creates ConfigMap


Step 6: STORE RELEASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Release info stored as Kubernetes Secret:
  ┌─────────────────────────────────────────┐
  │ Secret: sh.helm.release.v1.my-web-app.v1│
  │                                         │
  │ Contains:                               │
  │ • Chart metadata                        │
  │ • Values used                           │
  │ • Rendered manifests                    │
  │ • Release status (deployed/failed)      │
  │ • Timestamp                             │
  └─────────────────────────────────────────┘
```

---

## 📦 Chart Structure Deep Dive

```
📦 my-awesome-chart/
│
├── 📄 Chart.yaml              ← REQUIRED: Chart's ID card
│   ┌─────────────────────────────────────────────┐
│   │ apiVersion: v2                              │
│   │ name: my-awesome-chart                      │
│   │ description: A chart for my awesome app     │
│   │ type: application                           │
│   │ version: 1.2.3        ← Chart version      │
│   │ appVersion: "4.5.6"   ← App version        │
│   └─────────────────────────────────────────────┘
│
├── 📄 Chart.lock              ← Auto-generated dependency lock
│
├── 📄 values.yaml             ← IMPORTANT: Default configuration
│   ┌─────────────────────────────────────────────┐
│   │ replicaCount: 3                             │
│   │ image:                                      │
│   │   repository: nginx                         │
│   │   tag: "1.21"                               │
│   │ service:                                    │
│   │   type: ClusterIP                           │
│   │   port: 80                                  │
│   └─────────────────────────────────────────────┘
│
├── 📁 templates/              ← CORE: Kubernetes YAML templates
│   ├── 📄 deployment.yaml
│   ├── 📄 service.yaml
│   ├── 📄 ingress.yaml
│   ├── 📄 configmap.yaml
│   ├── 📄 _helpers.tpl       ← Template helper functions
│   ├── 📄 NOTES.txt          ← Post-install message
│   └── 📁 tests/
│       └── 📄 test-connection.yaml
│
├── 📁 charts/                 ← Sub-charts (dependencies)
│   ├── 📦 postgresql/
│   └── 📦 redis/
│
├── 📁 crds/                   ← Custom Resource Definitions
│
├── 📄 .helmignore             ← Files to exclude from package
│
└── 📄 README.md               ← Documentation
```

---

## 🎯 The Three Big Concepts

### Concept 1: Chart = The Blueprint

```
                        ┌─────────────────────┐
                        │     📦 CHART         │
                        │                     │
                        │  "Blueprint/Recipe" │
                        │                     │
                        │  Contains:          │
                        │  • Templates        │
                        │  • Default values   │
                        │  • Dependencies     │
                        │  • Metadata         │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
             ┌────────────┐ ┌────────────┐ ┌────────────┐
             │ Release A  │ │ Release B  │ │ Release C  │
             │ (dev)      │ │ (staging)  │ │ (prod)     │
             │ replica: 1 │ │ replica: 2 │ │ replica: 5 │
             └────────────┘ └────────────┘ └────────────┘
             
             One chart → Many releases with different configs!
```

### Concept 2: Release = A Running Instance

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  🚀 RELEASE = Chart installed on a cluster                   │
│                                                              │
│  Properties:                                                 │
│  ├── Name:      "my-web-app"                                │
│  ├── Namespace: "production"                                │
│  ├── Chart:     "my-chart v1.2.3"                           │
│  ├── Status:    "deployed"                                  │
│  ├── Revision:  3                                           │
│  └── Values:    { replicaCount: 5, image: "v2.0" }         │
│                                                              │
│  A release has a LIFECYCLE:                                  │
│                                                              │
│  install → upgrade → upgrade → rollback → uninstall         │
│    (v1)     (v2)      (v3)      (v2)       (gone)           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Concept 3: Repository = The App Store

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  📂 REPOSITORY = Collection of Charts                        │
│                                                              │
│  ┌──────────────────────────────────────┐                   │
│  │        Artifact Hub                  │                   │
│  │      (artifacthub.io)               │                   │
│  │                                      │                   │
│  │   🔍 Search across ALL repositories  │                   │
│  │                                      │                   │
│  │   Popular repos:                     │                   │
│  │   ├── bitnami/                       │                   │
│  │   │   ├── nginx                      │                   │
│  │   │   ├── postgresql                 │                   │
│  │   │   ├── redis                      │                   │
│  │   │   ├── wordpress                  │                   │
│  │   │   └── 100+ more                  │                   │
│  │   ├── prometheus-community/          │                   │
│  │   │   ├── prometheus                 │                   │
│  │   │   └── kube-prometheus-stack      │                   │
│  │   ├── grafana/                       │                   │
│  │   │   └── grafana                    │                   │
│  │   └── ingress-nginx/                 │                   │
│  │       └── ingress-nginx              │                   │
│  └──────────────────────────────────────┘                   │
│                                                              │
│  helm repo add bitnami https://charts.bitnami.com/bitnami  │
│  helm search repo nginx                                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Release Lifecycle Visualized

```
                    helm install
                         │
                         ▼
                  ┌──────────────┐
                  │  REVISION 1  │ ◄─── Status: deployed
                  │  v1.0.0      │
                  └──────┬───────┘
                         │
                    helm upgrade
                         │
                         ▼
                  ┌──────────────┐
                  │  REVISION 2  │ ◄─── Status: deployed
                  │  v1.1.0      │      (Rev 1 → superseded)
                  └──────┬───────┘
                         │
                    helm upgrade
                         │
                         ▼
                  ┌──────────────┐
                  │  REVISION 3  │ ◄─── Status: failed ❌
                  │  v1.2.0      │      (Rev 2 still running)
                  └──────┬───────┘
                         │
                    helm rollback 2
                         │
                         ▼
                  ┌──────────────┐
                  │  REVISION 4  │ ◄─── Status: deployed
                  │  (v1.1.0)    │      (Copy of Rev 2!)
                  └──────┬───────┘
                         │
                    helm uninstall
                         │
                         ▼
                  ┌──────────────┐
                  │   DELETED    │
                  │   All gone   │
                  └──────────────┘

Note: Rollback creates a NEW revision (4),
      it doesn't revert to revision 2.
      It COPIES rev 2's config into a new revision.
```

---

## 🔌 How Helm Talks to Kubernetes

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Helm uses YOUR kubeconfig to talk to Kubernetes             │
│                                                              │
│  ~/.kube/config                                              │
│  ┌────────────────────────────────────────┐                 │
│  │ clusters:                              │                 │
│  │ - name: my-cluster                     │                 │
│  │   server: https://k8s-api:6443         │                 │
│  │ users:                                 │                 │
│  │ - name: admin                          │                 │
│  │   token: xxxx                          │                 │
│  │ contexts:                              │                 │
│  │ - name: my-context                     │                 │
│  │   cluster: my-cluster                  │                 │
│  │   user: admin                          │                 │
│  │   namespace: default                   │                 │
│  └────────────────────────────────────────┘                 │
│                                                              │
│  Helm respects Kubernetes RBAC:                              │
│                                                              │
│  👤 User with limited access → Helm can only do what        │
│     that user can do in K8s                                  │
│                                                              │
│  👤 Cluster admin → Helm has full power                      │
│                                                              │
│  The kubeconfig context determines WHICH cluster             │
│  and namespace Helm operates on.                             │
│                                                              │
│  kubectl config current-context  ← Same context as Helm     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 Putting It All Together

```
     YOU                   HELM CLIENT               KUBERNETES
      │                        │                         │
      │  helm install          │                         │
      │  my-app bitnami/nginx  │                         │
      │───────────────────────►│                         │
      │                        │                         │
      │                  ┌─────┴─────┐                   │
      │                  │ 1. Fetch  │                   │
      │                  │    chart  │                   │
      │                  │ 2. Merge  │                   │
      │                  │    values │                   │
      │                  │ 3. Render │                   │
      │                  │    YAML   │                   │
      │                  │ 4. Valid- │                   │
      │                  │    ate    │                   │
      │                  └─────┬─────┘                   │
      │                        │                         │
      │                        │  Apply manifests        │
      │                        │────────────────────────►│
      │                        │                         │
      │                        │                   ┌─────┴─────┐
      │                        │                   │ Create:   │
      │                        │                   │ • Deploy  │
      │                        │                   │ • Service │
      │                        │                   │ • etc.    │
      │                        │                   └─────┬─────┘
      │                        │                         │
      │                        │  Store release secret   │
      │                        │────────────────────────►│
      │                        │                         │
      │  ✅ Release "my-app"   │                         │
      │  deployed!             │                         │
      │◄───────────────────────│                         │
      │                        │                         │
```

---

## 🧠 Knowledge Check

```
Q1: Does Helm 3 need a server component (Tiller)?
A:  No! Helm 3 is purely a client-side tool.
    It talks directly to the Kubernetes API.

Q2: Where does Helm store release information?
A:  As Kubernetes Secrets in the release's namespace.
    (Named: sh.helm.release.v1.<name>.v<revision>)

Q3: What's the difference between Chart version and App version?
A:  Chart version = version of the chart package itself
    App version = version of the application inside

Q4: Can you install the same chart twice?
A:  Yes! Each install creates a separate Release
    with a unique name.

Q5: What determines Helm's permissions?
A:  Your kubeconfig. Helm uses the same RBAC as
    your kubectl commands.
```

---

**Next → [Chapter 3: Installation & First Steps](03-installation.md)** ➡️
