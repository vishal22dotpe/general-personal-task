# Chapter 5: Templates & Go Templating Engine 🔧

## 🟡 INTERMEDIATE LEVEL

---

## 🎯 What is Helm Templating?

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Helm uses Go's text/template engine + Sprig library             │
│                                                                  │
│  Template + Values = Rendered Kubernetes YAML                    │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  TEMPLATE    │     │   VALUES     │     │  RENDERED    │    │
│  │              │     │              │     │  YAML        │    │
│  │  apiVersion: │     │              │     │              │    │
│  │   apps/v1   │     │ replicaCount:│     │ apiVersion:  │    │
│  │  replicas:   │  +  │   5          │  =  │  apps/v1    │    │
│  │   {{ .Values │     │              │     │ replicas: 5  │    │
│  │   .replica   │     │ image:       │     │ image:       │    │
│  │   Count }}   │     │  tag: "2.0"  │     │  myapp:2.0   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                                  │
│  Everything inside {{ }} is a template expression               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Built-in Objects (Data You Can Access)

```
┌──────────────────────────────────────────────────────────────────┐
│                  BUILT-IN OBJECTS MAP                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  {{ . }}  ← The ROOT object. Everything starts here.            │
│     │                                                            │
│     ├── .Values        → Your values.yaml + overrides           │
│     │   ├── .Values.replicaCount                                │
│     │   ├── .Values.image.repository                            │
│     │   └── .Values.service.port                                │
│     │                                                            │
│     ├── .Release       → Release information                    │
│     │   ├── .Release.Name           "my-app"                   │
│     │   ├── .Release.Namespace      "production"               │
│     │   ├── .Release.Revision       3                          │
│     │   ├── .Release.IsUpgrade      true/false                 │
│     │   ├── .Release.IsInstall      true/false                 │
│     │   └── .Release.Service        "Helm"                     │
│     │                                                            │
│     ├── .Chart         → Chart.yaml contents                    │
│     │   ├── .Chart.Name             "my-chart"                 │
│     │   ├── .Chart.Version          "1.2.3"                    │
│     │   ├── .Chart.AppVersion       "4.5.6"                    │
│     │   └── .Chart.Description      "A great chart"            │
│     │                                                            │
│     ├── .Capabilities  → Cluster capabilities                   │
│     │   ├── .Capabilities.KubeVersion.Version   "v1.28.0"     │
│     │   ├── .Capabilities.APIVersions.Has       check API      │
│     │   └── .Capabilities.HelmVersion           Helm ver       │
│     │                                                            │
│     ├── .Template      → Current template info                  │
│     │   ├── .Template.Name          "my-chart/templates/x.yaml"│
│     │   └── .Template.BasePath      "my-chart/templates"       │
│     │                                                            │
│     └── .Files         → Access non-template files              │
│         ├── .Files.Get "config.ini"                             │
│         ├── .Files.GetBytes "binary.dat"                        │
│         ├── .Files.Glob "configs/*.yaml"                        │
│         └── .Files.AsConfig                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔤 Template Syntax — From Basics to Advanced

### Level 1: Simple Value Substitution

```yaml
# Template:
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
  namespace: {{ .Release.Namespace }}
data:
  app-name: {{ .Chart.Name }}
  app-version: {{ .Chart.AppVersion }}
  replicas: {{ .Values.replicaCount | quote }}

# ──────────────────────────────────────────────
# With values.yaml: replicaCount: 5
# Release name: my-app, namespace: prod
# ──────────────────────────────────────────────

# Rendered:
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: prod
data:
  app-name: my-chart
  app-version: 4.5.6
  replicas: "5"          # quote wraps in quotes
```

### Level 2: Pipelines (Chaining Functions)

```yaml
# ═══════════════════════════════════════════════════════
# Pipes work like Unix pipes: value | function | function
# ═══════════════════════════════════════════════════════

# Pipe: value flows left → right through functions
data:
  # Simple pipe
  name: {{ .Values.appName | upper }}
  # "myapp" → "MYAPP"

  # Multiple pipes
  name: {{ .Values.appName | upper | quote }}
  # "myapp" → "MYAPP" → "\"MYAPP\""

  # Default value (if .Values.appName is empty)
  name: {{ .Values.appName | default "my-default-app" | quote }}

  # Trimming whitespace
  name: {{ .Values.appName | trim | upper }}

  # Truncate (max length)
  name: {{ .Values.appName | trunc 63 | trimSuffix "-" }}

# ═══════════════════════════════════════════════════════
# COMMON PIPE FUNCTIONS:
# ═══════════════════════════════════════════════════════
#
#  quote        → Wraps in double quotes
#  upper        → UPPERCASE
#  lower        → lowercase
#  title        → Title Case
#  trim         → Remove whitespace
#  trimSuffix   → Remove suffix
#  trimPrefix   → Remove prefix
#  trunc N      → Truncate to N characters
#  default VAL  → Use VAL if empty/nil
#  indent N     → Indent by N spaces
#  nindent N    → Newline + indent N spaces
#  toYaml       → Convert to YAML string
#  toJson       → Convert to JSON string
#  b64enc       → Base64 encode
#  b64dec       → Base64 decode
#  sha256sum    → SHA256 hash
#  replace      → String replace
#  contains     → Check if contains substring
#  hasPrefix    → Check prefix
#  hasSuffix    → Check suffix
```

### Level 3: Conditionals (if/else)

```yaml
# ═══════════════════════════════════════════════════════
# IF / ELSE IF / ELSE
# ═══════════════════════════════════════════════════════

# Basic if
spec:
  type: {{ .Values.service.type }}
  {{- if .Values.service.nodePort }}
  nodePort: {{ .Values.service.nodePort }}
  {{- end }}

# If/else
metadata:
  labels:
    env: {{ if eq .Values.environment "production" }}prod{{ else }}non-prod{{ end }}

# If/else if/else (multi-line, cleaner)
metadata:
  annotations:
    {{- if .Values.ingress.enabled }}
    kubernetes.io/ingress.class: nginx
    {{- else if .Values.service.type | eq "LoadBalancer" }}
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    {{- else }}
    app.kubernetes.io/managed-by: internal
    {{- end }}

# ═══════════════════════════════════════════════════════
# FALSY VALUES (these evaluate to false):
# ═══════════════════════════════════════════════════════
#
#  false          → boolean false
#  0              → zero number
#  ""             → empty string
#  nil / null     → nil value
#  []             → empty list
#  {}             → empty map
#
# EVERYTHING ELSE is truthy!

# ═══════════════════════════════════════════════════════
# COMPARISON OPERATORS:
# ═══════════════════════════════════════════════════════
#
#  eq   → equal               {{ if eq .Values.env "prod" }}
#  ne   → not equal           {{ if ne .Values.env "dev" }}
#  lt   → less than           {{ if lt .Values.count 5 }}
#  gt   → greater than        {{ if gt .Values.count 10 }}
#  le   → less or equal       {{ if le .Values.count 5 }}
#  ge   → greater or equal    {{ if ge .Values.count 10 }}
#  and  → logical AND         {{ if and .Values.a .Values.b }}
#  or   → logical OR          {{ if or .Values.a .Values.b }}
#  not  → logical NOT         {{ if not .Values.disabled }}
```

### Level 4: Loops (range)

```yaml
# ═══════════════════════════════════════════════════════
# RANGE — Iterate over lists and maps
# ═══════════════════════════════════════════════════════

# ──────── Iterating a LIST ────────
# values.yaml:
# environments:
#   - dev
#   - staging
#   - production

# Template:
data:
  environments: |
    {{- range .Values.environments }}
    - {{ . }}          # {{ . }} = current item
    {{- end }}

# Rendered:
data:
  environments: |
    - dev
    - staging
    - production


# ──────── Iterating a MAP ────────
# values.yaml:
# env:
#   DB_HOST: "postgres"
#   DB_PORT: "5432"
#   APP_ENV: "production"

# Template:
data:
  {{- range $key, $value := .Values.env }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}

# Rendered:
data:
  APP_ENV: "production"
  DB_HOST: "postgres"
  DB_PORT: "5432"


# ──────── Range with index ────────
# values.yaml:
# servers:
#   - name: web1
#     port: 8080
#   - name: web2
#     port: 8081

# Template:
{{- range $index, $server := .Values.servers }}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ $server.name }}-svc
spec:
  ports:
    - port: {{ $server.port }}
{{- end }}
```

### ⚠️ Understanding Whitespace Control

```yaml
# ═══════════════════════════════════════════════════════
# WHITESPACE CONTROL — Most confusing part of Helm! 🤯
# ═══════════════════════════════════════════════════════

# The Problem:
# ─────────────
data:
  greeting: "Hello"
  {{ if .Values.showName }}
  name: {{ .Values.name }}
  {{ end }}
  farewell: "Bye"

# Rendered (UGLY — extra blank lines!):
data:
  greeting: "Hello"
  
  name: John
  
  farewell: "Bye"


# The Solution: {{- and -}}
# ─────────────────────────

#  {{-  = eat whitespace BEFORE (left)
#  -}}  = eat whitespace AFTER (right)
#  {{-  -}} = eat whitespace BOTH sides

data:
  greeting: "Hello"
  {{- if .Values.showName }}
  name: {{ .Values.name }}
  {{- end }}
  farewell: "Bye"

# Rendered (CLEAN!):
data:
  greeting: "Hello"
  name: John
  farewell: "Bye"


# ═══════════════════════════════════════════════════════
# VISUAL EXPLANATION:
# ═══════════════════════════════════════════════════════
#
#  "Hello"\n  {{ if ... }}\n  "World"
#           ↑↑             ↑↑
#           These spaces and newlines are the problem!
#
#  "Hello"\n  {{- if ... }}\n  "World"
#           ↑↑
#           {{- eats this whitespace (left side)
#           Result: "Hello"{{ if ... }}\n  "World"
#
#  "Hello"\n  {{- if ... -}}\n  "World"
#                          ↑↑
#                          -}} eats this too (right side)
#           Result: "Hello""World"
#
# ═══════════════════════════════════════════════════════
# RULE OF THUMB:
#   {{- for control flow (if, range, end, define)
#   {{ without dash for actual output values
# ═══════════════════════════════════════════════════════
```

---

## 🔧 Functions Deep Dive

### String Functions

```yaml
# ═══════════════════════════════════════════════════════
# STRING FUNCTIONS (from Sprig library)
# ═══════════════════════════════════════════════════════

data:
  # Case conversion
  upper:    {{ "hello" | upper }}           # HELLO
  lower:    {{ "HELLO" | lower }}           # hello
  title:    {{ "hello world" | title }}     # Hello World
  
  # Trimming
  trimmed:  {{ "  hello  " | trim }}        # hello
  noSuffix: {{ "hello-" | trimSuffix "-" }} # hello
  noPrefix: {{ "-hello" | trimPrefix "-" }} # hello
  
  # Substring
  trunc:    {{ "abcdefgh" | trunc 5 }}      # abcde
  
  # Replace
  replaced: {{ "foo-bar" | replace "-" "_" }}  # foo_bar
  
  # Contains/Prefix/Suffix checks
  has:      {{ if contains "prod" .Values.env }}yes{{ end }}
  prefix:   {{ if hasPrefix "v" .Values.tag }}yes{{ end }}
  suffix:   {{ if hasSuffix ".io" .Values.host }}yes{{ end }}
  
  # Regex
  match:    {{ if regexMatch "^v[0-9]+$" .Values.tag }}valid{{ end }}
  
  # Printf-style formatting
  formatted: {{ printf "%s-%s" .Release.Name .Chart.Name }}
  
  # Quote (add double quotes)
  quoted:   {{ .Values.name | quote }}       # "value"
  squoted:  {{ .Values.name | squote }}      # 'value'
```

### Type Conversion

```yaml
# ═══════════════════════════════════════════════════════
# TYPE CONVERSION
# ═══════════════════════════════════════════════════════

data:
  # To string
  str:    {{ .Values.port | toString }}
  
  # To int
  num:    {{ "42" | atoi }}                  # string → int
  num64:  {{ int64 42 }}
  
  # To JSON
  json:   {{ .Values.config | toJson }}
  pjson:  {{ .Values.config | toPrettyJson }}
  
  # To YAML
  yaml: |
    {{ .Values.config | toYaml | nindent 4 }}
  
  # Base64
  encoded: {{ "secret" | b64enc }}           # c2VjcmV0
  decoded: {{ "c2VjcmV0" | b64dec }}         # secret
```

### List (Slice) Functions

```yaml
# ═══════════════════════════════════════════════════════
# LIST FUNCTIONS
# ═══════════════════════════════════════════════════════

# Create a list
{{ $myList := list "a" "b" "c" }}

# First and last
first: {{ first $myList }}         # a
last:  {{ last $myList }}          # c

# Append/Prepend
{{ $new := append $myList "d" }}   # [a b c d]
{{ $new := prepend $myList "z" }}  # [z a b c]

# Has (contains)
{{ if has "b" $myList }}yes{{ end }}  # yes

# Join
joined: {{ join "," $myList }}     # a,b,c

# Uniq (remove duplicates)
{{ list "a" "b" "a" "c" | uniq }}  # [a b c]

# Without (remove items)
{{ without $myList "b" }}          # [a c]
```

### Dict (Map) Functions

```yaml
# ═══════════════════════════════════════════════════════
# DICT (MAP) FUNCTIONS
# ═══════════════════════════════════════════════════════

# Create a dict
{{ $myDict := dict "name" "john" "age" "30" }}

# Get a value
name: {{ get $myDict "name" }}     # john

# Set a value
{{ $_ := set $myDict "email" "john@example.com" }}

# Has key
{{ if hasKey $myDict "name" }}yes{{ end }}

# Keys and Values
{{ keys $myDict }}                 # [name age email]
{{ values $myDict }}               # [john 30 john@...]

# Merge dicts (later overrides earlier)
{{ $merged := merge $dict1 $dict2 }}

# Deep copy
{{ $copy := deepCopy $myDict }}
```

---

## 🏗️ Named Templates & `_helpers.tpl`

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  _helpers.tpl = Reusable template snippets                      │
│                                                                  │
│  Problem: You repeat the same labels in EVERY template file:    │
│                                                                  │
│  deployment.yaml:           service.yaml:                       │
│  labels:                    labels:                              │
│    app: {{ .Chart.Name }}     app: {{ .Chart.Name }}            │
│    release: {{ .Release      release: {{ .Release               │
│      .Name }}                   .Name }}                         │
│    chart: {{ .Chart.Name     chart: {{ .Chart.Name              │
│      }}-{{ .Chart.Version      }}-{{ .Chart.Version             │
│      }}                        }}                                │
│                                                                  │
│  Solution: Define it ONCE in _helpers.tpl, use everywhere!      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Defining Named Templates

```yaml
# templates/_helpers.tpl

# ═══════════════════════════════════════════════════════
# Chart name (truncated for safety)
# ═══════════════════════════════════════════════════════
{{- define "my-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Full name (release name + chart name)
# ═══════════════════════════════════════════════════════
{{- define "my-chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Common labels
# ═══════════════════════════════════════════════════════
{{- define "my-chart.labels" -}}
helm.sh/chart: {{ include "my-chart.chart" . }}
{{ include "my-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Selector labels (used in deployment & service)
# ═══════════════════════════════════════════════════════
{{- define "my-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Chart label (name + version)
# ═══════════════════════════════════════════════════════
{{- define "my-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Service account name
# ═══════════════════════════════════════════════════════
{{- define "my-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "my-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

# ═══════════════════════════════════════════════════════
# Image reference (handles registry + repo + tag)
# ═══════════════════════════════════════════════════════
{{- define "my-chart.image" -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if .Values.image.registry -}}
{{ .Values.image.registry }}/{{ .Values.image.repository }}:{{ $tag }}
{{- else -}}
{{ .Values.image.repository }}:{{ $tag }}
{{- end -}}
{{- end }}
```

### Using Named Templates

```yaml
# templates/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-chart.fullname" . }}
  labels:
    {{- include "my-chart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-chart.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "my-chart.serviceAccountName" . }}
      containers:
        - name: {{ .Chart.Name }}
          image: {{ include "my-chart.image" . }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort | default 80 }}
```

### `include` vs `template`

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  {{ template "name" . }}  vs  {{ include "name" . }}             │
│                                                                  │
│  template:                                                       │
│  ├── Outputs text directly into the template                    │
│  ├── CANNOT be piped (no | nindent, | quote, etc.)              │
│  └── Rarely used in practice                                    │
│                                                                  │
│  include:                                                        │
│  ├── Returns text as a string                                   │
│  ├── CAN be piped! (| nindent 4, | quote, etc.)                │
│  └── ALWAYS use this! ✅                                        │
│                                                                  │
│  Example:                                                        │
│  ✅ {{ include "my-chart.labels" . | nindent 4 }}               │
│  ❌ {{ template "my-chart.labels" . | nindent 4 }}  ← BROKEN!  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔍 The `with` Block (Scope Change)

```yaml
# ═══════════════════════════════════════════════════════
# 'with' changes the scope (what '.' refers to)
# ═══════════════════════════════════════════════════════

# values.yaml:
# database:
#   host: postgres
#   port: 5432
#   name: mydb

# WITHOUT with (verbose):
env:
  - name: DB_HOST
    value: {{ .Values.database.host }}
  - name: DB_PORT
    value: {{ .Values.database.port | quote }}
  - name: DB_NAME
    value: {{ .Values.database.name }}

# WITH 'with' (cleaner):
{{- with .Values.database }}
env:
  - name: DB_HOST
    value: {{ .host }}           # . now means .Values.database
  - name: DB_PORT
    value: {{ .port | quote }}
  - name: DB_NAME
    value: {{ .name }}
{{- end }}

# ⚠️ GOTCHA: Inside 'with', you lose access to the root!
{{- with .Values.database }}
  host: {{ .host }}              # ✅ Works
  release: {{ .Release.Name }}   # ❌ ERROR! . is now database
  release: {{ $.Release.Name }}  # ✅ Use $ to access root!
{{- end }}

# $ = ALWAYS refers to the root scope
# . = Current scope (changes with 'with' and 'range')
```

---

## 📄 Working with Files (.Files)

```yaml
# ═══════════════════════════════════════════════════════
# Access non-template files in your chart
# ═══════════════════════════════════════════════════════

# Chart structure:
# my-chart/
# ├── config/
# │   ├── app.conf
# │   └── logging.conf
# ├── scripts/
# │   └── init.sh
# └── templates/
#     └── configmap.yaml

# ──────── Get file content ────────
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  app.conf: |
    {{ .Files.Get "config/app.conf" | nindent 4 }}

  init.sh: |
    {{ .Files.Get "scripts/init.sh" | nindent 4 }}

# ──────── Glob (multiple files) ────────
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-configs
data:
  {{- (.Files.Glob "config/*").AsConfig | nindent 2 }}
  # Creates one key per file, content as value

# ──────── As Secrets (base64) ────────
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-certs
type: Opaque
data:
  {{- (.Files.Glob "certs/*").AsSecrets | nindent 2 }}
  # Each file content is base64 encoded
```

---

## 🧪 Debugging Templates

```bash
# ═══════════════════════════════════════════════════════
# METHOD 1: --dry-run --debug (see rendered output)
# ═══════════════════════════════════════════════════════
helm install my-app ./my-chart --dry-run --debug

# ═══════════════════════════════════════════════════════
# METHOD 2: helm template (render locally, no cluster needed)
# ═══════════════════════════════════════════════════════
helm template my-app ./my-chart

# With specific values:
helm template my-app ./my-chart -f prod-values.yaml

# Show only one template:
helm template my-app ./my-chart -s templates/deployment.yaml

# ═══════════════════════════════════════════════════════
# METHOD 3: helm lint (check for errors)
# ═══════════════════════════════════════════════════════
helm lint ./my-chart

# With values:
helm lint ./my-chart -f prod-values.yaml

# ═══════════════════════════════════════════════════════
# METHOD 4: Get rendered manifests from a deployed release
# ═══════════════════════════════════════════════════════
helm get manifest my-app

# ═══════════════════════════════════════════════════════
# METHOD 5: Debug template expression (print to output)
# ═══════════════════════════════════════════════════════
# In your template, temporarily add:
# {{ .Values.myThing | toYaml }}
# {{ printf "%v" .Values.myThing }}
# This helps see what value you're working with
```

---

## 🧠 Knowledge Check

```
Q1: What does {{ .Values.image.tag | default .Chart.AppVersion | quote }} do?
A:  Gets image tag from values; if empty, uses Chart's appVersion;
    wraps the result in double quotes.

Q2: What's the difference between {{ and {{- ?
A:  {{  = normal, keeps whitespace before it
    {{- = trims all whitespace/newlines before it

Q3: How do you access the root scope inside a 'with' block?
A:  Use $ instead of .
    Example: {{ $.Release.Name }}

Q4: Why use 'include' instead of 'template'?
A:  'include' returns a string that can be piped to
    functions like nindent, quote, etc.
    'template' outputs directly and can't be piped.

Q5: What does the underscore in _helpers.tpl mean?
A:  Files starting with _ are NOT rendered as K8s resources.
    They're only used to define reusable template snippets.
```

---

**Next → [Chapter 6: Values & Configuration](06-values.md)** ➡️
