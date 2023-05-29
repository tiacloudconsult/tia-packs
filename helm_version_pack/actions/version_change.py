import subprocess
import yaml
import os
from typing import Any, Optional, Union
from yaml.loader import SafeLoader
from st2common.runners.base_action import Action


class VersionChange(Action):
    def __init__(self, git_url = "git@github.com:tiacloudconsult/tia-packs.git ",git_branch="st2-argocd-pack-dev" ):
        self.git_url = git_url
        self.git_branch = git_branch


    def clone(
            self, git_url : str,
            git_branch : str
    ) -> Any:
        # Clone the Git repository
        subprocess.call(["git", "clone", "-b", git_branch, git_url])

        # Get the name of the cloned directory
        cloned_dir = git_url.split("/")[-1].split(".")[0]

        # List the files in the cloned directory
        return os.listdir(cloned_dir)

   
    def change_chart_version(self):
        # files = self.clone(self.git_url, self.git_branch)
        with open("/setupst2_docker_vmount/k8s/Chart.yaml","r") as f:
            data = yaml.safe_load(f)
            version = data.get('version','0.0.0')
            major, minor, patch = map(int, version.split('.'))
            patch += 1  # Increment the patch version

        # Update data with the new version
        data['version'] = f'{major}.{minor}.{patch}'
        with open('/setupst2_docker_vmount/k8s/Chart.yaml','w') as f:
            yaml.dump(data,f)

    def main(self):
        return self.change_chart_version()



#   Get helm chart here
# https://github.com/tiacloudconsult/tia-packs/blob/st2-argocd-pack-dev/setupst2_docker_vmount/k8s/Chart.yaml


