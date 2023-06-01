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

class GitClone(Action):

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
    
    def git_clone(self, gitclone_repo_name, gitpush_repo_name):
                """It will clone both template repo and helm chart repo
                """

                #Block to read credentials from metadata service
                try:
                        application_name = "Centralized Logging Framework"
                        fa_pat=get_secret(application_name, "clm_fa_pat")
                        fa_usr=get_secret(application_name, "clm_fa_usr")
                        gitclone_branch=get_secret(application_name, "clm_gitclone_branch")

                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed("ERROR when reading stackstorm secrets.")
                
                cmdlist = ['mkdir /packs-workdir/observability_logstash_framework',
                'git -C /packs-workdir/observability_logstash_framework clone -b '+gitclone_branch+' https://'+fa_usr+':'+fa_pat+'@mygithub.gsk.com/gsk-tech/'+gitclone_repo_name+'.git',
                'git -C /packs-workdir/observability_logstash_framework clone -b main https://'+fa_usr+':'+fa_pat+'@mygithub.gsk.com/gsk-tech/'+gitpush_repo_name+'.git'
                ]

                try:

                        for command in cmdlist:
                                code, out, err = self.run_command(command)
                                logger.info('COMMAND: '+command+' OUT: '+out+' ERR: '+err)

                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed("ERROR WHILE RUNNING GIT COMMANDS")   

    def run(self, gitclone_repo_name, gitpush_repo_name):

            """main function
            """

            self.git_clone(gitclone_repo_name, gitpush_repo_name)