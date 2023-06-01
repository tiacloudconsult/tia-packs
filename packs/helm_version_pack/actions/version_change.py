import subprocess
import yaml
import os
from typing import Any, Optional, Union
from yaml.loader import SafeLoader
from st2common.runners.base_action import Action


# noinspection PyInterpreter
class VersionChange(Action):
    def __init__(self, git_url = "git@github.com:tiacloudconsult/tia-packs.git ",git_branch="st2-argocd-pack-dev" ):
        super(VersionChange, self).__init__(git_url, git_branch)
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
    def read_yaml_file(self, file_path: str) -> Any:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    def write_yaml_file(self, data: Any, file_path: str) -> None:
        with open(file_path, "w") as f:
            yaml.dump(data, f)

    def increment_patch_version(self, version: str) -> str:
        major, minor, patch = map(int, version.split('.'))
        patch += 1  # Increment the patch version
        return f'{major}.{minor}.{patch}'

    def change_chart_version(self) -> None:
        chart_file_path = "/setupst2_docker_vmount/k8s/Chart.yaml"
        data = self.read_yaml_file(chart_file_path)
        version = data.get('version', '0.0.0')
        new_version = self.increment_patch_version(version)
        data['version'] = new_version
        self.write_yaml_file(data, chart_file_path)

    def push_changes_to_github(self) -> None:
        subprocess.call(["git", "add", "."])
        subprocess.call(["git", "commit", "-m", "Updated version in Chart.yaml"])
        subprocess.call(["git", "push"])

   def main(self)->None:
       """
        Entry point for executing the action.
        Changes the version in the Chart.yaml file.
        """
       self.change_chart_version()
       self.push_changes_to_github()






#   Get helm chart here
# https://github.com/tiacloudconsult/tia-packs/blob/st2-argocd-pack-dev/setupst2_docker_vmount/k8s/Chart.yaml


