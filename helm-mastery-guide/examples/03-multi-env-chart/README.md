# Example 3: Multi-Environment Deployment 🌍

## 🟡 Intermediate Level

Demonstrates how to use one chart across multiple environments
(dev, staging, production) with different values files.

## What You'll Learn
- Environment-specific values files
- Values merge order & priorities
- The `--set` override for CI/CD
- Best practices for multi-env configuration

## Structure
```
03-multi-env-chart/
├── Chart.yaml
├── values.yaml                ← Shared defaults
├── values-dev.yaml            ← Dev overrides
├── values-staging.yaml        ← Staging overrides
├── values-prod.yaml           ← Production overrides
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

## How The Values Merge

```
Default (values.yaml):    replicaCount: 1, logLevel: info
Dev (values-dev.yaml):    replicaCount: 1, logLevel: debug
Staging:                  replicaCount: 2, logLevel: info
Production:               replicaCount: 5, logLevel: warn

Deploy command:
  helm install my-app ./03-multi-env-chart -f values-prod.yaml
  
  Result: values.yaml defaults + values-prod.yaml overrides merged
```

## Try It!

```bash
# Dev environment
helm template my-app ./03-multi-env-chart -f 03-multi-env-chart/values-dev.yaml

# Staging environment
helm template my-app ./03-multi-env-chart -f 03-multi-env-chart/values-staging.yaml

# Production environment
helm template my-app ./03-multi-env-chart -f 03-multi-env-chart/values-prod.yaml

# Production + CI/CD image tag override
helm template my-app ./03-multi-env-chart \
  -f 03-multi-env-chart/values-prod.yaml \
  --set image.tag=v2.5.0

# Compare environments
diff <(helm template app ./03-multi-env-chart -f 03-multi-env-chart/values-dev.yaml) \
     <(helm template app ./03-multi-env-chart -f 03-multi-env-chart/values-prod.yaml)
```
