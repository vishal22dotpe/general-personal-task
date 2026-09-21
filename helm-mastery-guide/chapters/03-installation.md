# Chapter 3: Installation & First Steps 🚀

## 🟢 BEGINNER LEVEL

---

## 📥 Installing Helm

### Method 1: Script Install (Easiest - Linux/macOS)

```bash
# Download and run the official install script
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Method 2: Package Managers

```bash
# macOS (Homebrew)
brew install helm

# Ubuntu/Debian (Snap)
sudo snap install helm --classic

# Ubuntu/Debian (APT)
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | \
  sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/helm.gpg] \
  https://baltocdn.com/helm/stable/debian/ all main" | \
  sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# Windows (Chocolatey)
choco install kubernetes-helm

# Windows (Scoop)
scoop install helm

# Windows (Winget)
winget install Helm.Helm
```

### Method 3: Binary Download

```bash
# 1. Download from https://github.com/helm/helm/releases
# 2. Unpack:  tar -zxvf helm-v3.x.x-linux-amd64.tar.gz
# 3. Move:    mv linux-amd64/helm /usr/local/bin/helm
```

### Verify Installation

```bash
helm version

# Output should be something like:
# version.BuildInfo{
#   Version:"v3.15.x",
#   GitCommit:"xxx",
#   GoVersion:"go1.22.x"
# }
```

---

## 🔧 Prerequisites Check

```
┌──────────────────────────────────────────────────────────────┐
│                 PREREQUISITES CHECKLIST                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ 1. kubectl installed and configured                      │
│        kubectl version --client                              │
│                                                              │
│  ✅ 2. Kubernetes cluster accessible                         │
│        kubectl cluster-info                                  │
│                                                              │
│        Options for local cluster:                            │
│        ┌─────────────────────────────────────┐              │
│        │  • minikube   (minikube start)      │              │
│        │  • kind       (kind create cluster) │              │
│        │  • k3d        (k3d cluster create)  │              │
│        │  • Docker Desktop (enable K8s)      │              │
│        │  • Rancher Desktop                  │              │
│        └─────────────────────────────────────┘              │
│                                                              │
│  ✅ 3. kubeconfig setup (~/.kube/config)                     │
│        kubectl config current-context                        │
│                                                              │
│  ✅ 4. Helm installed                                        │
│        helm version                                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎬 Your First Helm Experience!

### Step 1: Add a Chart Repository

```bash
# Add the official Bitnami repository (most popular)
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repo index (like apt update)
helm repo update

# See your repos
helm repo list
```

```
Visualization of what happened:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Your Machine                    Internet
  ┌──────────────┐               ┌──────────────────────┐
  │ Helm Client  │───repo add──→│ bitnami chart repo   │
  │              │               │                      │
  │ Local Index: │◄──downloads──│ index.yaml           │
  │ bitnami/     │               │ (list of all charts) │
  │  ├── nginx   │               └──────────────────────┘
  │  ├── redis   │
  │  ├── mysql   │
  │  └── 100+... │
  └──────────────┘
```

### Step 2: Search for Charts

```bash
# Search in your added repos
helm search repo nginx
helm search repo postgresql

# Search on Artifact Hub (internet)
helm search hub wordpress
```

```
Output example:
━━━━━━━━━━━━━━━

NAME                  CHART VERSION   APP VERSION   DESCRIPTION
bitnami/nginx         18.1.5          1.27.0        NGINX Open Source for Kubernetes
bitnami/nginx-...     ...             ...           ...
```

### Step 3: Inspect a Chart Before Installing

```bash
# See chart info
helm show chart bitnami/nginx

# See ALL default values (very useful!)
helm show values bitnami/nginx

# See the README
helm show readme bitnami/nginx

# See everything
helm show all bitnami/nginx
```

```
Why inspect first?
━━━━━━━━━━━━━━━━━

  helm show values bitnami/nginx

  Shows you EVERY configurable option:
  ┌──────────────────────────────────────────┐
  │ replicaCount: 1          ← How many pods │
  │ image:                                   │
  │   registry: docker.io                    │
  │   repository: bitnami/nginx              │
  │   tag: 1.27.0                           │
  │ service:                                 │
  │   type: LoadBalancer     ← Service type  │
  │   port: 80                               │
  │ resources:                               │
  │   limits:                                │
  │     cpu: 150m                            │
  │     memory: 256Mi                        │
  │ ...hundreds more options...              │
  └──────────────────────────────────────────┘
```

### Step 4: Install Your First Chart! 🎉

```bash
# Install nginx with default values
helm install my-nginx bitnami/nginx

# ──────────────────────────────────────
# Breakdown:
#   helm install     → The command
#   my-nginx         → YOUR release name (you pick this!)
#   bitnami/nginx    → The chart (repo/chart-name)
# ──────────────────────────────────────
```

```
What happens:
━━━━━━━━━━━━━

  helm install my-nginx bitnami/nginx
       │          │          │
       │          │          └── Which chart to install
       │          │
       │          └── Name for this release (unique per namespace)
       │
       └── The install command

  ┌──────────────────────────────────────────────────────────┐
  │ Output:                                                  │
  │                                                          │
  │ NAME: my-nginx                                           │
  │ LAST DEPLOYED: Mon Sep 21 10:30:00 2026                 │
  │ NAMESPACE: default                                       │
  │ STATUS: deployed                                         │
  │ REVISION: 1                                              │
  │ TEST SUITE: None                                         │
  │ NOTES:                                                   │
  │ ** Please be patient while the chart is being deployed **│
  │                                                          │
  │ NGINX can be accessed through the following DNS name:    │
  │   my-nginx.default.svc.cluster.local                     │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Step 5: Check What You Deployed

```bash
# List all releases
helm list
# or
helm ls

# Get detailed status
helm status my-nginx

# See what K8s resources were created
kubectl get all -l app.kubernetes.io/instance=my-nginx
```

```
helm list output:
━━━━━━━━━━━━━━━━━

NAME       NAMESPACE  REVISION  STATUS    CHART          APP VERSION
my-nginx   default    1         deployed  nginx-18.1.5   1.27.0
```

---

## 🔧 Common Install Variations

```bash
# ═══════════════════════════════════════════════════════
# 1. Install with custom values via --set
# ═══════════════════════════════════════════════════════
helm install my-nginx bitnami/nginx \
  --set replicaCount=3 \
  --set service.type=ClusterIP

# ═══════════════════════════════════════════════════════
# 2. Install with a values file
# ═══════════════════════════════════════════════════════
# First create: my-values.yaml
# replicaCount: 3
# service:
#   type: ClusterIP

helm install my-nginx bitnami/nginx -f my-values.yaml

# ═══════════════════════════════════════════════════════
# 3. Install in a specific namespace
# ═══════════════════════════════════════════════════════
helm install my-nginx bitnami/nginx \
  --namespace web \
  --create-namespace

# ═══════════════════════════════════════════════════════
# 4. Install a specific chart version
# ═══════════════════════════════════════════════════════
helm install my-nginx bitnami/nginx --version 15.0.0

# ═══════════════════════════════════════════════════════
# 5. Dry run (see what WOULD happen, don't actually do it)
# ═══════════════════════════════════════════════════════
helm install my-nginx bitnami/nginx --dry-run --debug

# ═══════════════════════════════════════════════════════
# 6. Generate a release name automatically
# ═══════════════════════════════════════════════════════
helm install bitnami/nginx --generate-name

# ═══════════════════════════════════════════════════════
# 7. Wait for all resources to be ready
# ═══════════════════════════════════════════════════════
helm install my-nginx bitnami/nginx --wait --timeout 5m
```

---

## 🔄 Upgrade, Rollback, Uninstall

```bash
# ═══════════════════════════════════════════════════════
# UPGRADE a release
# ═══════════════════════════════════════════════════════
helm upgrade my-nginx bitnami/nginx --set replicaCount=5

# ═══════════════════════════════════════════════════════
# See HISTORY
# ═══════════════════════════════════════════════════════
helm history my-nginx

# REVISION  STATUS       CHART          DESCRIPTION
# 1         superseded   nginx-18.1.5   Install complete
# 2         deployed     nginx-18.1.5   Upgrade complete

# ═══════════════════════════════════════════════════════
# ROLLBACK to a previous revision
# ═══════════════════════════════════════════════════════
helm rollback my-nginx 1

# ═══════════════════════════════════════════════════════
# UNINSTALL (delete everything)
# ═══════════════════════════════════════════════════════
helm uninstall my-nginx
```

```
Visual Flow:
━━━━━━━━━━━━

  install        upgrade          rollback 1       uninstall
     │              │                │                │
     ▼              ▼                ▼                ▼
  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
  │ Rev1 │───→│ Rev2 │───→│ Rev3 │───→│ Gone │
  │deploy│    │deploy│    │deploy│    │      │
  │ r=1  │    │ r=5  │    │ r=1  │    └──────┘
  └──────┘    └──────┘    └──────┘
                            (copy of Rev1)
```

---

## 🧪 Practice Exercise

```
╔══════════════════════════════════════════════════════════════╗
║                    HANDS-ON EXERCISE                         ║
║              "Your First Helm Journey"                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Add the bitnami repo                                     ║
║     helm repo add bitnami https://charts.bitnami.com/bitnami║
║                                                              ║
║  2. Search for Redis                                         ║
║     helm search repo redis                                   ║
║                                                              ║
║  3. Inspect Redis chart values                               ║
║     helm show values bitnami/redis | head -50                ║
║                                                              ║
║  4. Install Redis                                            ║
║     helm install my-redis bitnami/redis \                    ║
║       --set architecture=standalone                          ║
║                                                              ║
║  5. Check the release                                        ║
║     helm list                                                ║
║     helm status my-redis                                     ║
║     kubectl get pods                                         ║
║                                                              ║
║  6. Upgrade (change replica count)                           ║
║     helm upgrade my-redis bitnami/redis \                    ║
║       --set architecture=standalone \                        ║
║       --set replica.replicaCount=2                           ║
║                                                              ║
║  7. Check history                                            ║
║     helm history my-redis                                    ║
║                                                              ║
║  8. Rollback                                                 ║
║     helm rollback my-redis 1                                 ║
║                                                              ║
║  9. Clean up                                                 ║
║     helm uninstall my-redis                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🧠 Knowledge Check

```
Q1: How do you add a chart repository?
A:  helm repo add <name> <url>

Q2: How do you see available values before installing?
A:  helm show values <chart>

Q3: What's the difference between --set and -f?
A:  --set: individual value overrides on command line
    -f: a YAML file with all your overrides

Q4: How do you install in a specific namespace?
A:  --namespace <ns> --create-namespace

Q5: What does --dry-run do?
A:  Shows what WOULD be deployed without actually
    deploying. Great for testing!
```

---

**Next → [Chapter 4: Charts Deep Dive](04-charts-deep-dive.md)** ➡️
