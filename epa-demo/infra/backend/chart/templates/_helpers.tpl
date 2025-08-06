{{- define "backend.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "backend.fullname" -}}
{{ .Release.Name }}-{{ include "backend.name" . }}
{{- end }}