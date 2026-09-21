{{- define "multi-env-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "multi-env-app.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "multi-env-app.labels" -}}
app.kubernetes.io/name: {{ include "multi-env-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
environment: {{ .Values.config.environment | default "unknown" }}
{{- end }}

{{- define "multi-env-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "multi-env-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
