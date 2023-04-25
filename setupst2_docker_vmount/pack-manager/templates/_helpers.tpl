{{- define "pack-manager.name" -}}
    {{- if .Values.appendReleaseName -}}
        {{- cat .Release.Name "-" .Values.name -}}
    {{- else -}}
        {{- "pack-manager" -}}
    {{- end -}}
{{- end -}}