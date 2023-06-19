# Pack to assign port and patch kong-proxy deployment and service yamls with the assigned port.

```sh
# url: http://st2.dev.tiacloud.io/
# user: st2admin passwd: tiacloud!2!

# To install pack on K8s
st2 pack install file:///opt/stackstorm/packs/tia/<pack_name>


```sh
#Run this webhook to trigger the action 'kong_tcp_trigger' 
# You get the St2-Api-Key from azure key vault 'argocd-tfs-kvault'. Secret name is st2-api-key-dev

curl -X POST http://st2.dev.tiacloud.io/api/v1/webhooks/kong_tcp_trigger -H "Content-Type: application/json" -H "St2-Api-Key: <>" -d '{
  "git_branch": "dev",
  "port_var": "3000"
}'

curl -X POST http://127.0.0.1:82/api/v1/webhooks/kong_tcp_trigger -H "Content-Type: application/json" -H "St2-Api-Key: <>" -d '{
  "git_branch": "dev",
  "port_var": "3000"
}'
