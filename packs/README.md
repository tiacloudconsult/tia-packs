# Pack to generated various jinja2 based templates for ArgoCD and Terraform

```sh
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

curl -X POST http://localhost:82/api/v1/webhooks/argocd_trigger -H "Content-Type: application/json" -H "St2-Api-Key: <>" -d '{
  "git_branch": "argocd-jinja2-crossplane-tf-demo",
  "config_template": "config.j2",
  "config_file": "config.yml",
  "yaml_template": "namespace_config.j2",
  "yaml_file": "namespaces.yaml",
  "input_vars": {
    "teamName": "fork",
    "server": "test3",
    "environment": "dev-dev",
    "token": "hello",
    "ca": "yea"
  }
}'