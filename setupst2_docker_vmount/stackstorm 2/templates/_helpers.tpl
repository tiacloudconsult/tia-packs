# consolidate pack-configs-volumes definitions
{{- define "st2-config-volume" -}}
- name: st2-config-vol
  configMap:
    name: {{ $.Release.Name }}-st2-config
# Additions:
- name: st2-base-config
  configMap:
    name: {{ .Release.Name }}-base-config
{{- end -}}

{{- define "st2-config-volume-mounts" -}}
- name: st2-config-vol
  mountPath: /etc/st2/st2.docker.conf
  subPath: st2.docker.conf
- name: st2-config-vol
  mountPath: /etc/st2/st2.user.conf
  subPath: st2.user.conf
# Additions:
- name: st2-base-config
  mountPath: /etc/st2/st2.conf
  subPath: st2.conf
{{- end -}}