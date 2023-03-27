import os
import subprocess

from st2common.runners.base_action import Action

class CloneAndListAction(Action):
    def run(self, git_url, git_branch):
        # Clone the Git repository
        subprocess.call(["git", "clone", "-b", git_branch, git_url])

        # Get the name of the cloned directory
        cloned_dir = git_url.split("/")[-1].split(".")[0]

        # List the files in the cloned directory
        files = os.listdir(cloned_dir)
        return files