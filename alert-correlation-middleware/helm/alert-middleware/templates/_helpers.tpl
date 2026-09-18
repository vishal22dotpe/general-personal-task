{{/*
Expand the name of the chart.
*/}}
{{- define "alert-middleware.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "alert-middleware.fullname" -}}
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

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "alert-middleware.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "alert-middleware.labels" -}}
helm.sh/chart: {{ include "alert-middleware.chart" . }}
{{ include "alert-middleware.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "alert-middleware.selectorLabels" -}}
app.kubernetes.io/name: {{ include "alert-middleware.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service account name
*/}}
{{- define "alert-middleware.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "alert-middleware.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret name (support existing secret)
*/}}
{{- define "alert-middleware.secretName" -}}
{{- if .Values.existingSecret }}
{{- .Values.existingSecret }}
{{- else }}
{{- include "alert-middleware.fullname" . }}-secrets
{{- end }}
{{- end }}

{{/*
Redis URL — use bundled redis or external
*/}}
{{- define "alert-middleware.redisUrl" -}}
{{- if .Values.redis.enabled }}
redis://{{ include "alert-middleware.fullname" . }}-redis:6379/0
{{- else }}
{{- .Values.config.redisUrl }}
{{- end }}
{{- end }}
