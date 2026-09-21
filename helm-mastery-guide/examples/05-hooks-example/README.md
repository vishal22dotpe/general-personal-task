# Example 5: Helm Hooks Demo 🪝

## 🔴 Advanced Level

Demonstrates Helm hooks: pre-install, post-install, and test hooks
with proper annotations, weights, and delete policies.

## What You'll Learn
- Creating hook Jobs with annotations
- Hook weights (execution order)
- Hook delete policies (cleanup)
- Helm tests as hooks

## Hook Execution Order

```
helm install my-release ./05-hooks-example
    │
    ▼
┌──────────────────────────────┐
│ pre-install Job (weight: -5) │  ← Runs FIRST (simulates DB migration)
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Main ConfigMap created       │  ← Normal resource
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ post-install Job (weight: 5) │  ← Runs LAST (verification)
└──────────────────────────────┘

helm test my-release
    │
    ▼
┌──────────────────────────────┐
│ Smoke test Pod               │  ← Validates deployment
└──────────────────────────────┘
```

## Try It!

```bash
# See all rendered resources including hooks
helm template my-release ./05-hooks-example

# Render only the pre-install hook
helm template my-release ./05-hooks-example -s templates/pre-install-job.yaml

# Disable hooks in render
helm template my-release ./05-hooks-example --set hooks.preInstall.enabled=false

# Install (needs cluster — hooks will actually execute!)
helm install my-release ./05-hooks-example

# Run tests
helm test my-release --logs
```
