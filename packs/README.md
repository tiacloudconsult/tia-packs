# Pack to generated various jinja2 based templates for ArgoCD and Terraform

```sh
# To install pack on K8s
st2 pack install file:///opt/stackstorm/packs/tia/argocd_trigger
# Inputs are based on the below

"git_branch": "<branch_name>"
  
# 'config_template' is being appended unto this path argocd/argocdv2.0_templates/master_j2config/
"config_template": "config.j2"
# 'config_file' is also being appended unto this path argocd/argocdv2.0_templates/master_j2config/
"config_file": "config.yml"
# 'yaml_template' is also being appended unto this path argocd/argocdv2.0_templates/master_j2config/
"yaml_template": "<filename>.j2"
# 'yaml_template' is being appended unto this path argocd/master/
"yaml_file": "<filename>.yaml",
# this is a list of dictionaries which will be used by the .j2 files
"input_vars": {
    "teamName": "fork"
{

```sh
#Run this webhook to trigger the action 'argocd_trigger' 
# You get the St2-Api-Key from azure key vault 'argocd-tfs-kvault'. Secret name is st2-api-key-dev

curl -X POST http://st2.dev.tiacloud.io/api/v1/webhooks/argocd_trigger -H "Content-Type: application/json" -H "St2-Api-Key: <>" -d '{
  "git_branch": "dev",
  "config_template": "config.j2",
  "config_file": "config.yml",
  "yaml_template": "cluster_roles.j2",
  "yaml_file": "cluster_roles.yaml",
  "argocdapp_template": "argocd_deploy_config.j2",
  "argocdapp_file": "argocd-rbac-dev.yaml",
  "input_vars": {
    "Permission": "contributor",
    "get": "get",
    "watch": "watch",
    "list": "list",
    "server": "https://aks-dns-vs966uez.hcp.eastus.azmk8s.io:443",
    "AppPath": "k8s-rbac"
  }
}'

curl -X POST http://127.0.0.1:82//api/v1/webhooks/argocd_trigger -H "Content-Type: application/json" -H "St2-Api-Key: <>" -d '{
  "git_branch": "dev",
  "config_template": "config.j2",
  "config_file": "config.yml",
  "yaml_template": "rolebindings.j2,",
  "yaml_file": "rolebindings.yaml",
  "argocdapp_template": "argocd_deploy_config.j2",
  "argocdapp_file": "argocd-rbac-dev.yaml",
  "input_vars": {
    "environment": "dev",
    "groupObjectid": "e2ba6951-aff4-4492-a450-e51da7b0abdb",
    "Namespace":"st2-dev",
    "server": "https://aks-dns-vs966uez.hcp.eastus.azmk8s.io:443",
    "AppPath": "k8s-rbac"
  }
}'