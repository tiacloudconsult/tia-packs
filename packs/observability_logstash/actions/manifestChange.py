import subprocess
import yaml
from yaml.loader import SafeLoader
from st2common.runners.base_action import Action
from packs.utility.actions.get_secret import get_secret

from error import Operationfailed

import logging,sys
import ecs_logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)

class ManifestChange(Action):

        def run_command(self, cmd):
                """_summary_

                Args:
                cmd (str): Shell script to run

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

        
        def manifest(self, gitpush_repo_name):
                """
                Connect with Argo cd Cluster to update deployment version in Application
                """

                #Block to read credentials from metadata service
                try:
                        application_name = "Centralized Logging Framework"
                        server=get_secret(application_name, "clm_argocd_server")
                        argocd_usr=get_secret(application_name, "clm_argocd_usr")
                        argocd_pass=get_secret(application_name, "clm_argocd_pass")
                        logstash_pipeline_app=get_secret(application_name, "clm_logstash_pipeline_app")
                        
                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed("ERROR when reading stackstorm secrets")

                # It will read the updated version from Chart.yaml and store it in a variable
                with open('/packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/Chart.yaml') as f:
                        data = yaml.load(f, Loader=SafeLoader)
                        version = str(data['version'])

                        logger.info(f"version:{version}")
                
                # It will login to argocd server and update the version in application deployment
                cmdlist = ['yes | argocd login '+server+' --username '+argocd_usr+' --password '+argocd_pass+' --grpc-web',
                '''argocd app patch '''+logstash_pipeline_app+''' --patch '{"spec": { "source": { "targetRevision": "'''+version+'''" } }}' --type merge''',
                ]

                for command in cmdlist:
                        code, out, err = self.run_command(command)
                        logger.info('OUT: '+out+' ERR: '+err)
                        
                error_message = "Error doing Manifest Changes"
                if (code==0):
                        logger.info("Manifest changes are applied")
                else:
                        logger.error(error_message,extra={"error.message":error_message,"error.code":code})
                        raise Operationfailed(error_message)

        def run(self, gitpush_repo_name):

                """main function
                """  

                self.manifest(gitpush_repo_name)


