import os
import subprocess
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from st2common.runners.base_action import Action

class CloneGitRepoAction(Action):
    def run(self, config_template, config_file, git_branch, input_vars):
        # Retrieve the Git credentials from StackStorm keys
        git_username = 'tiacloud-gh'
        git_password = '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'

        # Set the Git username and email
        email_command = 'git config --global user.email "francis.poku@tiacloud.io"'
        name_command = 'git config --global user.name "tiacloud-gh"'
        email_result = subprocess.run(email_command, shell=True, capture_output=True)
        name_result = subprocess.run(name_command, shell=True, capture_output=True)
        if email_result.returncode != 0:
            raise Exception('Failed to set Git email: {}'.format(email_result.stderr.decode()))
        if name_result.returncode != 0:
            raise Exception('Failed to set Git username: {}'.format(name_result.stderr.decode()))

        # Define the Git repository URL and clone the repository
        git_url = 'https://'+git_username+':'+git_password+'@github.com/tiacloudconsult/mec-argocd-dev.git'

        # Check if the 'gen' directory exists. If it exists, delete it and recreate before cloning the repository
        file_path = '/tmp/gen/'
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
        os.mkdir(file_path)

        git_command = 'git clone -b {} {} {}'.format(git_branch, git_url, file_path)
        clone_result = subprocess.run(git_command, shell=True, capture_output=True, cwd=file_path)
        if clone_result.returncode != 0:
            raise Exception('Failed to clone Git repository: {}'.format(clone_result.stderr.decode()))

        # Parse the JSON config data and generate the configuration file using the Jinja2 template
        config_data = json.loads(json.dumps(input_vars))
        env = Environment(loader=FileSystemLoader('./tmp//argocd/j2_templates/master_j2config'))
        template = env.get_template(config_template)
        config_data['username'] = git_username
        config_data['password'] = git_password
        config_content = template.render(config_data)

        # Save the configuration file to disk
        config_path = os.path.join(file_path, 'argocd/j2_templates/master_j2config/', config_file)
        with open(config_path, 'w') as f:
            f.write(config_content)

        # Commit and push the changes
        os.chdir(file_path)
        subprocess.run('git add .', shell=True)
        commit_result = subprocess.run('git commit -m "Updated config file"', shell=True, capture_output=True)
        if commit_result.returncode != 0:
            raise Exception('Failed to commit changes: {}'.format(commit_result.stderr.decode()))
        push_result = subprocess.run('git push', shell=True, capture_output=True)
        if push_result.returncode != 0:
            raise Exception('Failed to push changes: {}'.format(push_result.stderr.decode()))

        # Remove the cloned repository directory
        shutil.rmtree(file_path)