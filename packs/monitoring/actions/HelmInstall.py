import subprocess
import sys
from jinja2 import Environment, FileSystemLoader
from st2client.client import Client
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action
import logging, sys
import ecs_logging
from datetime import datetime, timezone
import requests
from error import operationfailed
from packs.utility.actions.get_secret_vm import get_secret

command_variable = "\n COMMAND: "
error_variable = "ERROR: "
kube_config = ' --kubeconfig='
app_name = "Centralized Monitoring Framework"
project_path = "/opt/stackstorm/"
cfg = project_path+'config-file/config'
rmdir_str = 'rm -rf '
values_str = '/values_'
git_c = 'git -C '

class HelmInstall(Action):
        def __init__(self, **kwargs):
                self.logger = logging.getLogger("app")
                self.logger.setLevel(logging.DEBUG)
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(ecs_logging.StdlibFormatter())
                self.logger.addHandler(handler)
                self.logger_json = {
                        "tags": ["prometheus","helm","stackstorm"],
                        "labels": {"action": "prometheus helm install"},
                        "business_unit": "R&D Tech",
                        "solution_group": "Emerging Tech, Architecture, & AI",
                        "product_family": "Quality Engineering and Design",
                        "PRODUCT": "DevSecOps",
                        "ENVIRONMENT": "Dev",
                        "APPLICATION_NAME": app_name, 
                        "APPLICATION_OWNER_POC": "Andrew.x.Dalmeny@gsk.com"
                }
        
        def logger_exception(self, stmt, error_message):
                self.logger_json["error.message"] = error_message

                self.logger.exception(stmt, extra = self.logger_json)

        def logger_info(self, stmt):
                self.logger_json["error.message"] = ""

                self.logger.info(stmt, extra = self.logger_json)
        
        def run_command(self, cmd):
                """_summary_

                Args:
                cmd (str): Shell command to run

                Returns:
                returncode (int)
                stdout (str)
                stderr (str)
                """
                proc = subprocess.Popen(cmd,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
                )
                stdout, stderr = proc.communicate()

                return proc.returncode, stdout.rstrip().decode('ascii'), stderr.rstrip().decode('ascii')

        def generate_j2(self, data, src, target, tmplt_path):
                
                try:
                        #Load config file template and render with data values
                        env = Environment(loader=FileSystemLoader(tmplt_path),
                                        trim_blocks=True, lstrip_blocks=True)
                        template = env.get_template(src)
                        file = open(target, "w")
                        file.write(template.render(data))
                        file.close()
                except Exception as e:
                        self.logger_exception("ERROR WHEN CREATING FROM TEMPLATE: ", str(e))
                        raise operationfailed("ERROR when creating from template: "+e)
                return 0

        def get_secrets(self, vaultname):
                """Connect to cluster and run helm install

                Raises:
                Generic Exception 1: Error in az login, az keyvault commands
                Cluster variables Exception: Raised if any of the cluster secrets are null
                Generic Exception 2: Error in config file cp or helm commands
                """
                ca = server = serviceaccount = token = None
                
                #Block to read credentials of az service principal from stackstorm server
                try:
                        sp_username = get_secret(app_name, "monitoring_sp_username")
                        sp_password = get_secret(app_name, "monitoring_sp_password")
                        sp_tenant = get_secret(app_name, "monitoring_sp_tenant")
                        mimir_ip = get_secret(app_name, "monitoring_mimir_server")
                        docker_server = get_secret(app_name, "monitoring_docker_server")
                        docker_username = get_secret(app_name, "monitoring_docker_username")
                        docker_password = get_secret(app_name, "monitoring_docker_password")
                        fa_pat = get_secret(app_name, "monitoring_fa_pat")
                except Exception as e:
                        self.logger_exception("ERROR when reading metadata secrets: ", str(e))
                        raise operationfailed("ERROR when reading metadata secrets: ", e)

                secrets_user_vault = ['SERVER',
                'CA',
                'SERVICE-ACCOUNT',
                'TOKEN']

                # List of commands containing az login, az keyvault secret show
                cmd_list = ['az login --service-principal --username '+sp_username+' --password '+sp_password+' --tenant '+sp_tenant+' --allow-no-subscriptions']

                for secret in secrets_user_vault:
                        cmd_list.append('az keyvault secret show --name '+secret+' --vault-name '+vaultname+' --query value | tr -d \'"\'')
                cmd_list.append('az logout')
            
                # Loop through commands and assign secrets into variables
                for command in cmd_list:
                        code, out, err = self.run_command(command)
                        if err != '' and 'warning' not in err.lower() and err!="b''":
                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed (error_variable+err+command_variable+command)
                        if ' SERVER ' in command:
                                server = out
                        elif ' CA ' in command:
                                ca = out
                        elif ' SERVICE-ACCOUNT ' in command:
                                serviceaccount = out
                        elif ' TOKEN ' in command:
                                token = out
                
                if (ca is None or server is None or serviceaccount is None or token is None):
                        self.logger_exception("ERROR when reading cluster variables: ", "Cluster variables are not set. Please check secrets and azure connection")
                        raise operationfailed('Cluster variables are not set. Please check secrets and azure connection')
                
                return 0, server, ca, serviceaccount, token, docker_server, docker_username, docker_password, fa_pat, mimir_ip
        
        def get_config(self, server, ca, serviceaccount, token, fa_pat, clustername):

                fa_usr = get_secret(app_name, "monitoring_fa_usr")
                fa_email = get_secret(app_name, "monitoring_fa_email")
                archive_branch = get_secret(app_name, "monitoring_archive_branch")
                repo_name = get_secret(app_name, "monitoring_prometheus_repo")
                
                cmd_list = [rmdir_str+project_path+'config-file',
                        rmdir_str+project_path+repo_name,
                        'git clone -b '+archive_branch+' https://'+fa_usr+':'+fa_pat+'@mygithub.gsk.com/gsk-tech/'+repo_name+'.git',
                        'mkdir config-file']
                tmplt_path = project_path+repo_name+'/templates'

                for command in cmd_list:
                        code, out, err = self.run_command(command)
                        print('COMMAND: '+command+' OUT: '+out+' ERR: '+err)
                        if err != '' and 'warning' not in err.lower() and 'Cloning into' not in err:
                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed (error_variable+err+command_variable+command)

                data = {
                        "Cluster_Name": clustername,
                        "ca": ca,
                        "server": server,
                        "serviceAccount": serviceaccount,
                        "token": token
                }

                self.generate_j2(data, 'k8s-config.j2', 'config-file/config',tmplt_path)

                return 0, tmplt_path, fa_usr, fa_email, archive_branch, repo_name
        
        def check_prometheus(self, namespace):
                prometheus_found = False
                namespace_found = False

                cmd_dict ={0: 'kubectl get ns '+namespace+kube_config+cfg+' | grep '+namespace,
                        1: 'helm list -n '+namespace+kube_config+cfg+' | grep prometheus'}
                
                for key in cmd_dict:
                        command = cmd_dict[key]
                        code, out, err = self.run_command(command)
                        print('COMMAND: '+command+' OUT: '+out+' ERR: '+err)
                        if err != '' and 'warning' not in err.lower() and 'namespaces "'+namespace+'" not found' not in err:
                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed(error_variable+err+command_variable+command)
                        if code==0:
                                if key==0:
                                        namespace_found = True
                                elif key==1:
                                        prometheus_found = True
                
                if namespace_found and not prometheus_found:
                        command = 'kubectl delete ns '+namespace+kube_config+cfg
                        code, out, err = self.run_command(command)
                        print('COMMAND: '+command+' OUT: '+out+' ERR: '+err)
                        if err != '' and 'warning' not in err.lower():
                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed(error_variable+err+command_variable+command)
                
                return 0, prometheus_found

        def get_values(self, mimir_ip, clustername, business_unit, solution_group, product_family, product_name, tmplt_path, repo_name, fa_usr, fa_email, archive_branch):

                business_unit = business_unit.replace('&','\&')
                solution_group  = solution_group.replace('&','\&')
                product_family = product_family.replace('&','\&')
                product_name = product_name.replace('&','\&')

                now = datetime.now()
                timestamp = now.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")

                cmd_list = ['sed -e s/mimir_IP/"'+mimir_ip+'"/g -e s/tenant_ID/"'+clustername+'"/g -e s/business_unit_value/"'+business_unit+'"/g -e s/solution_group_value/"'+solution_group+'"/g -e s/product_family_value/"'+product_family+'"/g -e s/product_name_value/"'+product_name+'"/g -e s/cluster_name_value/"'+clustername+'"/g '+tmplt_path+'/values.yaml > '+tmplt_path+values_str+clustername+'_'+timestamp+'.yaml',
                   'cp '+tmplt_path+values_str+clustername+'_'+timestamp+'.yaml '+project_path+repo_name+'/values_archive/',
                   git_c+'"'+project_path+repo_name+'/" config user.email '+fa_email,
                   git_c+'"'+project_path+repo_name+'/" config user.name '+fa_usr,
                   git_c+'"'+project_path+repo_name+'/" add values_archive/values_'+clustername+'_'+timestamp+'.yaml',
                   git_c+'"'+project_path+repo_name+'/" commit -m "pushing prometheus values file"',
                   git_c+'"'+project_path+repo_name+'/" push'
                   ]

                for command in cmd_list:
                        code, out, err = self.run_command(command)
                        if err != '' and 'warning' not in err.lower() and 'Everything up-to-date' not in err and archive_branch+' -> '+archive_branch not in err:
                                self.logger_exception("COMMAND: "+command, err)
                                raise Exception (error_variable+err+command_variable+command)
                return 0, timestamp

        def prometheus_helm_install(self, name, namespace, tmplt_path, docker_server, docker_username, docker_password, clustername, timestamp):
                                
                #List of commands to check existing Prometheus installation, and run helm repo add, helm install, and cleanup
                cmd_dict = {0: 'kubectl create ns '+namespace+kube_config+cfg,
                1: 'kubectl create secret docker-registry imgcredacr --namespace '+namespace+' --docker-server='+docker_server+' --docker-username='+docker_username+' --docker-password='+docker_password+kube_config+cfg,
                2: 'helm repo add prometheus-community https://prometheus-community.github.io/helm-charts'+kube_config+cfg+' --force-update',
                3: 'helm install '+name+' --values '+tmplt_path+values_str+clustername+'_'+timestamp+'.yaml --namespace '+namespace+' --create-namespace prometheus-community/kube-prometheus-stack --version 35.5.1'+kube_config+cfg,
                4: 'kubectl delete secret imgcredacr --namespace '+namespace+kube_config+cfg
                }

                for key in cmd_dict:
                        command = cmd_dict[key]
                        code, out, err = self.run_command(command)
                        print("COMMAND: "+command+ " OUT: "+out+" ERR: "+err)
                        if (err != '' and 'warning' not in err.lower()) or ('warning' in err.lower() and 'error' in err.lower()):
                                if 'helm' in command:
                                        self.logger_exception("ERROR in helm: ", "Failed to install chart. Please check error details")

                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed (error_variable+err+command_variable+command)

                self.logger_info("Prometheus install completed successfully")
                return 0


        def cleanup(self):
                cmd_list = [rmdir_str+project_path+'config-file',
                rmdir_str+project_path+'qed-op-monitoring-framework-prometheus']

                for command in cmd_list:
                        code, out, err = self.run_command(command)
                        print('COMMAND: '+command+' OUT: '+out+' ERR: '+err)
                        if err != '' and 'warning' not in err.lower() and 'Cloning into' not in err:
                                self.logger_exception("COMMAND: "+command, err)
                                raise operationfailed (error_variable+err+command_variable+command)

        
        def run(self, clustername, vaultname, business_unit, solution_group, product_family, product_name, name="prometheus", namespace="prometheus"):

                """main function

                Args:
                clusterName (str): Target cluster name
                vaultName (str): Vault location of cluster secrets
                name (str): Name of helm release (Optional). Default prometheus
                namespace (str): Target namespace (Optional). Default prometheus

                """
                self.logger_info("Reading secrets")
                code, server, ca, serviceaccount, token, docker_server, docker_username, docker_password, fa_pat, mimir_ip = self.get_secrets(vaultname)

                if code==0:
                        self.logger_info("Generating config file")
                        code = 1
                        code, tmplt_path, fa_usr, fa_email, archive_branch, repo_name = self.get_config(server, ca, serviceaccount, token, fa_pat, clustername)

                if code==0:
                        self.logger_info("Checking for existing Prometheus")
                        code = 1
                        code, prometheus_found = self.check_prometheus(namespace)

                if not prometheus_found:
                        if code==0:
                                self.logger_info("Generating values file")
                                code = 1
                                code, timestamp = self.get_values(mimir_ip, clustername, business_unit, solution_group, product_family, product_name, tmplt_path, repo_name, fa_usr, fa_email, archive_branch)

                        if code==0:
                                self.logger_info("Installing Prometheus")
                                code = 1
                                code = self.prometheus_helm_install(name, namespace, tmplt_path, docker_server, docker_username, docker_password, clustername, timestamp)
                else:
                        self.logger_info("Prometheus installation already exists")

                self.logger_info("Calling Cleanup")
                self.cleanup()
