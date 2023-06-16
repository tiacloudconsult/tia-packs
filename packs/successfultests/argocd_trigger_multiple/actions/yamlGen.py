import os
import subprocess
import pathlib
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from st2common.runners.base_action import Action
import sys
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class CloneGitRepoAction(Action):
    def run(self, yaml_template, yaml_file, git_branch, input_vars):

        tenant_id = '36fdb665-cb69-41f6-8bf1-03e5a0887e79'
        # Replace with your service principal client ID
        client_id = 'c083190a-d0b6-4e93-a771-6553dc68fb8c'
        # Replace with your service principal client secret
        client_secret = 'jTk8Q~1-lApIXqFFsNuGcttL2H6P24H53.Oboa23'
        # Replace with your Key Vault URL
        vault_url = 'https://argocd-tfs-kvault.vault.azure.net/'
        # Replace with the name of your secret
        secret_name = 'git-pat-st2-dev'

        try:
            # Create a credential object using service principal credentials
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )

            # Create a secret client
            client = SecretClient(vault_url=vault_url, credential=credential)

            # Retrieve the secret value
            secret = client.get_secret(secret_name)
            secret_value = secret.value

            # Store the secret value in the variable
            git_password = secret_value

            # Print the retrieved secret value
            print(f"Retrieved secret value: {git_password}")

        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

        # Retrieve the Git credentials from StackStorm keys
        git_username = 'tiacloud-gh'
        git_password = secret_value

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
        env = Environment(loader=FileSystemLoader(file_path + 'argocd/j2_templates/master_j2config'))

        config_data['username'] = git_username
        config_data['password'] = git_password

        base_dir = 'argocd/apps/'
        # Split the yaml_template and yaml_file strings into lists
        yaml_template = yaml_template.split(", ")
        yaml_file = yaml_file.split(", ")

        # Iterate over key-value pairs in input_vars
        for key, values in config_data.items():
            # Skip keys that are not relevant for mapping to templates and files
            if key not in ["teamName", "environment"]:
                continue

            # Convert single values to a list
            if not isinstance(values, list):
                values = [values]

            # Iterate over the values and map them to the corresponding templates and files
            for value, yaml_templates, yaml_files in zip(values, yaml_template, yaml_file):
                # Update temp_config_data with current value
                temp_config_data = config_data.copy()
                temp_config_data[key] = value

                # Render YAML template
                template = env.get_template(yaml_templates)
                config_content = template.render(temp_config_data)

                # Write YAML content to file
                file_name = os.path.splitext(yaml_files)[0]
                directory_name = file_name.split('.')[0]
                config_path = pathlib.Path(file_path, base_dir, directory_name, yaml_files)
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    f.write(config_content)

        # Commit and push the changes
        os.chdir(file_path)
        subprocess.run('git add .', shell=True)
        subprocess.run('git commit -m "Updated config files"', shell=True, capture_output=True)
        subprocess.run('git push', shell=True, capture_output=True)

        # Remove the cloned repository directory
        shutil.rmtree(file_path)