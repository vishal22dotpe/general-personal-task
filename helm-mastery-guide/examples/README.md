# 🛠️ Hands-On Practice Examples

These are complete, working Helm chart examples that you can render
and study. Each example builds on concepts from the chapters.

## Examples List

| # | Example | Level | Concepts Covered |
|---|---------|-------|------------------|
| 1 | [Basic Chart](01-basic-chart/) | 🟢 Beginner | Chart.yaml, values, simple templates, pipes |
| 2 | [Nginx Chart](02-nginx-chart/) | 🟡 Intermediate | Full chart: deployment, service, ingress, HPA, helpers, tests |
| 3 | [Multi-Env Chart](03-multi-env-chart/) | 🟡 Intermediate | Environment-specific values (dev/staging/prod) |
| 5 | [Hooks Demo](05-hooks-example/) | 🔴 Advanced | Pre/post install hooks, hook weights, tests |

## How to Use These Examples

### Without a Kubernetes Cluster (Template Mode)

You don't need a running cluster to learn from these examples!
Use `helm template` to render them locally:

```bash
# Render any example
helm template my-release ./examples/01-basic-chart
helm template my-release ./examples/02-nginx-chart
helm template my-release ./examples/03-multi-env-chart -f examples/03-multi-env-chart/values-prod.yaml

# Render a specific template
helm template my-release ./examples/02-nginx-chart -s templates/deployment.yaml

# Lint to check for errors
helm lint ./examples/01-basic-chart
helm lint ./examples/02-nginx-chart
```

### With a Kubernetes Cluster (Full Install)

```bash
# Install example 1
helm install test-basic ./examples/01-basic-chart

# Install example 2 with custom values
helm install test-nginx ./examples/02-nginx-chart --set replicaCount=2

# Install example 3 for production
helm install test-prod ./examples/03-multi-env-chart -f examples/03-multi-env-chart/values-prod.yaml

# Clean up
helm uninstall test-basic test-nginx test-prod
```

## Learning Path

```
Start with Example 1 (basic)
       │
       ▼
Study Example 2 (see how a real chart is built)
       │
       ▼
Try Example 3 (multi-env is crucial for real work)
       │
       ▼
Study Example 5 (hooks for advanced workflows)
       │
       ▼
🏆 Build your own chart from scratch!
```
