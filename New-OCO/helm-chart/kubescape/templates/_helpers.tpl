{{/*
Expand the name of the chart.
*/}}
{{- define "kubescape.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kubescape.fullname" -}}
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
{{- define "kubescape.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kubescape.labels" -}}
helm.sh/chart: {{ include "kubescape.chart" . }}
{{ include "kubescape.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kubescape.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubescape.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "kubescape.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "kubescape.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "cronjob.schedule" -}}
{{- if .Values.cronjob.schedule }}
{{ .Values.cronjob.schedule }}
{{- else -}}
{{- $interval := .Values.cronjob.interval -}}
{{- if hasSuffix "m" $interval -}}
*/{{ trimSuffix "m" $interval }} * * * *
{{- else if hasSuffix "h" $interval -}}
0 */{{ trimSuffix "h" $interval }} * * *
{{- else if hasSuffix "d" $interval -}}
0 0 */{{ trimSuffix "d" $interval }} * *
{{- else -}}
*/5 * * * * # fallback
{{- end -}}
{{- end }}
{{- end }}

