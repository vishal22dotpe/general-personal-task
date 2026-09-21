# Example 1: Hello Helm — Your First Chart 🎯

## 🟢 Beginner Level

This is the simplest possible Helm chart. It creates just one ConfigMap
to teach you the fundamentals.

## What You'll Learn
- Chart structure (Chart.yaml, values.yaml, templates/)
- Value substitution `{{ .Values.xxx }}`
- Built-in objects (`.Release`, `.Chart`)
- Pipe functions (`quote`, `upper`, `default`)
- Range loops
- NOTES.txt

## Chart Structure
```
01-basic-chart/
├── Chart.yaml              ← Chart identity
├── values.yaml             ← Default values
├── README.md               ← This file
└── templates/
    ├── configmap.yaml      ← Our one template
    └── NOTES.txt           ← Post-install message
```

## Try It!

```bash
# Render template locally (no cluster needed!)
helm template my-first-release ./01-basic-chart

# Install (needs a cluster)
helm install my-first-release ./01-basic-chart

# Override values
helm template my-first-release ./01-basic-chart \
  --set greeting="Namaste" \
  --set name="Bhai"

# See the rendered output
helm template my-first-release ./01-basic-chart \
  --set extraSettings.color=red \
  --set extraSettings.language=hi \
  --set extraSettings.mood=happy
```

## Exercises

1. **Change the greeting**: Use `--set greeting="Your message"` and re-render
2. **Add a new value**: Add `author: "your-name"` to values.yaml and use it in the configmap
3. **Try nesting**: Add `app.version` and `app.port` as nested values
4. **Break it intentionally**: Remove a `}}` and run `helm lint` to see the error
