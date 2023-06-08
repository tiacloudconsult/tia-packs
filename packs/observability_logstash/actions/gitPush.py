import subprocess
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

class GitPush(Action):

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
    
    def git_push(self, gitpush_repo_name, gitclone_repo_name):
                """
                1. It will copy the values file form template repo and paste it into the helm chart repo
                2. It will create and update packages according to new version
                3. Then finally it will push the changes into helm chart repo
                """

                #Block to read credentials from metadata service
                try:
                        application_name = "Centralized Logging Framework"
                        fa_usr=get_secret(application_name, "clm_fa_usr")
                        fa_email=get_secret(application_name, "clm_fa_email")

                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed("ERROR when reading stackstorm secrets")

                # List of commands 
                git_command = 'git -C "/packs-workdir/observability_logstash_framework/'
                cmdlist = ['cp /packs-workdir/observability_logstash_framework/'+gitclone_repo_name+'/src/templates/values.yaml /packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/charts/logstash/',
                'helm package /packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/ -d /packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/packages',
                'helm repo index /packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/packages',
                git_command+gitpush_repo_name+'/" config  user.email '+fa_email,
                git_command+gitpush_repo_name+'/" config  user.name '+fa_usr,
                git_command+gitpush_repo_name+'/" add .',
                git_command+gitpush_repo_name+'/" commit -m "Create package"',
                git_command+gitpush_repo_name+'/" push'
                ]

                try:

                        for command in cmdlist:
                                code, out, err = self.run_command(command)
                                logger.info('COMMAND: '+command+' OUT: '+out+' ERR: '+err)

                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed("ERROR WHILE RUNNING GIT COMMANDS")   

    def run(self, gitpush_repo_name, gitclone_repo_name):

            """main function
            """

            self.git_push(gitpush_repo_name, gitclone_repo_name)