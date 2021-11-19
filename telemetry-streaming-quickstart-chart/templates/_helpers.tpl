{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "telemetry-quickstart.promscale.connection-string" -}}
{{- printf "postgresql://%s:%s@timescaledb-svc/postgres" .Values.timescaledb.username .Values.timescaledb.password | b64enc }}
{{- end }}