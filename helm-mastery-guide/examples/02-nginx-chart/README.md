# Example 2: Complete Nginx Chart 🌐

## 🟡 Intermediate Level

A production-ready Nginx chart with all the common patterns:
deployment, service, ingress, HPA, configmap, service account, and tests.

## What You'll Learn
- _helpers.tpl and named templates (define/include)
- Conditional resources (if/with)
- The `with` scope change & `$` root accessor
- Complex range loops (ingress TLS/hosts)
- toYaml + nindent pattern
- Autoscaling toggle
- Helm tests
- NOTES.txt with conditional output

## Chart Structure
```
02-nginx-chart/
├── Chart.yaml
├── values.yaml
├── README.md
└── templates/
    ├── _helpers.tpl           ← Named templates
    ├── deployment.yaml        ← Pod controller
    ├── service.yaml           ← Network exposure
    ├── ingress.yaml           ← External routing (optional)
    ├── hpa.yaml               ← Autoscaling (optional)
    ├── configmap.yaml         ← Custom nginx config (optional)
    ├── serviceaccount.yaml    ← RBAC identity
    ├── NOTES.txt              ← Post-install info
    └── tests/
        └── test-connection.yaml
```

## Try It!

```bash
# Render with defaults
helm template my-nginx ./02-nginx-chart

# Render with 3 replicas
helm template my-nginx ./02-nginx-chart --set replicaCount=3

# Render with ingress enabled
helm template my-nginx ./02-nginx-chart \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mysite.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix

# Render with autoscaling
helm template my-nginx ./02-nginx-chart --set autoscaling.enabled=true

# Render with custom nginx config
helm template my-nginx ./02-nginx-chart --set customConfig.enabled=true

# Only render the deployment
helm template my-nginx ./02-nginx-chart -s templates/deployment.yaml

# Lint the chart
helm lint ./02-nginx-chart
```

## Exercises

1. **Add a PodDisruptionBudget**: Create `pdb.yaml` with condition `pdb.enabled`
2. **Add environment variables**: Support `env` map in values → inject as container env
3. **Add a sidecar container**: Support optional sidecar (e.g., fluentd log shipper)
4. **Create a values-prod.yaml**: Override for production (more replicas, more resources, HPA on)
5. **Add a health endpoint ConfigMap**: Serve a custom health page at /healthz
