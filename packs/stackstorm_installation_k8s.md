# StackStorm Kubernetes HA Installation
```sh
### Prequistes ###

# git clone https://github.com/tiacloudconsult/mec-argocd-dev.git
# Run Cronjob in mec-argocd-dev/argocd/app/st2-dev/jobs/st2-fileshare-dev-auth-job.yml to deploy secrets required for PVC
# Deploy PV and PVC using mec-argocd-dev/argocd/app/st2-dev/persistence/st2-fileshare-pv.yml 

### ST2 Deployment ###

# git clone https://github.com/stackstorm/stackstorm-k8s
# make changes to the values.yml for the below replicas so count is = 1
``rabbitmq, mongodb``

# make changes to the values.yml to mount shared path '/opt/stackstorm/pack/tia' for theses st2 components st2api, st2workflowengine, st2actionrunner, st2sensorcontainer, st2client, and st2garbagecollector

  # extra_volumes:
  #   - name: packs
  #     mount:
  #       mountPath: "/opt/stackstorm/packs/tia"
  #       subPath: tia  # the subpath allows multiple pods to mount without giving autonomy to any one pods to claim the filesystem
  #       readOnly: false
  #     volume:
  #       persistentVolumeClaim:
  #         claimName: pvc-st2-packs

  # env:
  #   PACKS_PATH: "/opt/stackstorm/packs/tia"

 # make changes to the values.yml to mount shared path '/opt/stackstorm/config' for theses st2 components st2auth, st2auth, and st2notifier

  # extra_volumes:
  #   - name: configs
  #     mount:
  #       mountPath: "/opt/stackstorm/configs"
  #       subPath: configs
  #       readOnly: false
  #     volume:
  #       persistentVolumeClaim:
  #         claimName: pvc-st2-pack-configs

 # make changes to the values.yml to mount shared path '/opt/stackstorm/virtualenvs' for theses st2 components st2actionrunner, st2sensorcontainer

  # extra_volumes:
  #   - name: virtualenvs
  #     mount:
  #       mountPath: "/opt/stackstorm/virtualenvs"
  #       subPath: virtualenvs
  #       readOnly: false
  #     volume:
  #       persistentVolumeClaim:
  #         claimName: pvc-st2-virtualenvs

# make changes to the values.yml to configure ingress

# ingress:
#   # As recommended, ingress is disabled by default.
#   enabled: true
#   # Annotations are used to configure the ingress controller
#   annotations:
# #   cert-argocd.io/issuer: letsencrypt-production
#     ingress.kubernetes.io/ssl-redirect: "false"
#     nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
#     kubernetes.io/ingress.class: "nginx"
#     nginx.ingress.kubernetes.io/rewrite-target: /
#   # Map hosts to paths
#   hosts:
#   - host: st2.dev.tiacloud.io
#     # Map paths to services
#     paths:
#       - path: /
#         serviceName: stackstorm-ha-<release_name>-st2web  #based on the helm release_name
#         servicePort: 80

# Install ST2
``helm install -f values.yaml --generate-name stackstorm/stackstorm-ha --namespace st2-dev --timeout 59m0s``
``kubectl get pods -n st2-dev -w``
# If a change made in values.yaml, then run below command.
``helm upgrade stackstorm-ha-<release_name> stackstorm/stackstorm-ha -f values.yaml``

# Create st2_api_key
``kubectl exec stackstorm-ha-1681832811-st2client -it bash``
``st2 apikey create -k -m '{"used_by": "my integration"}'``

# To Install your 'Packs', add the name of your pack to the below configmap, and commit and push it to git. 
``mec-argocd-dev/argocd/app/st2-dev/configmaps/st2-pack-install-cm.yml``
# There is a cronjob (st2-pack-install-cronjob) that runs every 5mins to install any new packs. 

## Installation fo Packs can be viewed here:
# url: http://st2.dev.tiacloud.io/
# user: st2admin passwd: tiacloud!2!