{{/*
Expand the name of the chart.
*/}}
{{- define "infrawatch.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "infrawatch.fullname" -}}
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
{{- define "infrawatch.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "infrawatch.labels" -}}
helm.sh/chart: {{ include "infrawatch.chart" . }}
{{ include "infrawatch.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "infrawatch.selectorLabels" -}}
app.kubernetes.io/name: {{ include "infrawatch.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Component-specific selector labels
*/}}
{{- define "infrawatch.componentLabels" -}}
{{ include "infrawatch.selectorLabels" . }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "infrawatch.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "infrawatch.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return the image name for a component
Usage: {{ include "infrawatch.image" (dict "image" .Values.backend.image "global" .Values.global) }}
*/}}
{{- define "infrawatch.image" -}}
{{- $registry := .global.imageRegistry | default "" -}}
{{- $repo := .image.repository -}}
{{- $tag := .image.tag | default "latest" -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry $repo $tag -}}
{{- else -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
{{- end }}

{{/*
MongoDB connection URL — prefer explicit secret, fall back to building from sub-chart values
*/}}
{{- define "infrawatch.mongodbUrl" -}}
{{- if .Values.backend.secrets.mongodbUrl -}}
{{- .Values.backend.secrets.mongodbUrl -}}
{{- else -}}
{{- $host := printf "%s-mongodb" (include "infrawatch.fullname" .) -}}
{{- $user := .Values.mongodb.auth.username | default "infrawatch" -}}
{{- $pass := .Values.mongodb.auth.password -}}
{{- $db := .Values.mongodb.auth.database | default "infrawatch" -}}
{{- printf "mongodb://%s:%s@%s:27017/%s?authSource=admin" $user $pass $host $db -}}
{{- end -}}
{{- end }}

{{/*
Redis URL — prefer explicit secret, fall back to sub-chart service name
*/}}
{{- define "infrawatch.redisUrl" -}}
{{- if .Values.backend.secrets.redisUrl -}}
{{- .Values.backend.secrets.redisUrl -}}
{{- else -}}
{{- $host := printf "%s-redis-master" (include "infrawatch.fullname" .) -}}
{{- printf "redis://%s:6379/0" $host -}}
{{- end -}}
{{- end }}

{{/*
RabbitMQ URL — prefer explicit secret, fall back to sub-chart service name
*/}}
{{- define "infrawatch.rabbitmqUrl" -}}
{{- if .Values.backend.secrets.rabbitmqUrl -}}
{{- .Values.backend.secrets.rabbitmqUrl -}}
{{- else -}}
{{- $host := printf "%s-rabbitmq" (include "infrawatch.fullname" .) -}}
{{- $user := .Values.rabbitmq.auth.username | default "infrawatch" -}}
{{- $pass := .Values.rabbitmq.auth.password -}}
{{- printf "amqp://%s:%s@%s:5672/" $user $pass $host -}}
{{- end -}}
{{- end }}
