import os
import subprocess
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader, Template
from st2common.runners.base_action import Action
import sys
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class CloneGitRepoAction(Action):
    def run(self, git_branch, port_var):
        # Replace with your Azure AD tenant ID
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

        # Define the path to the YAML file
        kong_file = "kong-deployment-tiacourses.yaml"
        yaml_file = os.path.join(file_path, 'argocd/apps/kong/', kong_file)
        # Define the Jinja2 template
        template = """
            - env:
                - name: KONG_STREAM_LISTEN
                  value: "{{ updated_value }}"
        """
        # Define the containerPort template
        container_port_template = """
                - containerPort: {{ port }}
                  name: stream{{ port }}
                  protocol: TCP
        """
        # Define the service template
        service_template = """
        - name: stream{{ port }}
            port: {{ port }}
            protocol: TCP
            targetPort: {{ port }}
        """
        # Define the port value
        port = f"{port_var}"  # Replace with your desired port

        # Load the YAML file with multiple documents
        with open(yaml_file, "r") as file:
            documents = list(yaml.safe_load_all(file))

        # Update the KONG_STREAM_LISTEN value in the Deployment document
        for data in documents:
            if data is not None and "kind" in data and data["kind"] == "Deployment":
                containers = data.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
                for container in containers:
                    env_list = container.get("env", [])
                    for env in env_list:
                        if env.get("name") == "KONG_STREAM_LISTEN":
                            current_value = env.get("value", "")
                            updated_value = f"{current_value}, 0.0.0.0:{port}"
                            env["value"] = updated_value

                            # Render the Jinja2 template and append it to the YAML document
                            container_template = Template(container_port_template)
                            rendered_template = container_template.render(port=port)
                            container.setdefault("ports", []).extend(yaml.safe_load(rendered_template))

            # Update the ports in the Service document
            if data is not None and "kind" in data and data["kind"] == "Service":
                ports = data.get("spec", {}).get("ports", [])
                ports.append({"name": f"stream{port}", "port": int(port), "protocol": "TCP", "targetPort": int(port)})

        # Write the updated YAML documents back to the file
        with open(yaml_file, "w") as file:
            for index, document in enumerate(documents):
                if document is not None:
                    yaml.dump(document, file, default_flow_style=False)
                    if index < len(documents) - 1:
                        file.write("---\n")  # Add --- between multiple documents


        # Remove --- at the end of the last YAML document
        with open(yaml_file, "r+") as file:
            lines = file.readlines()
            if lines and lines[-1] == "---\n":
                file.seek(0)
                file.truncate()
                file.writelines(lines[:-1])

        # Commit and push the changes
        os.chdir(file_path)
        subprocess.run('git add .', shell=True)
        subprocess.run('git commit -m "Updated config file"', shell=True, capture_output=True)
        subprocess.run('git push', shell=True, capture_output=True)

        # Remove the cloned repository directory
        shutil.rmtree(file_path)

        print("Configuration update complete.")

        # Run additional commands
        install_argocd_command = "curl -sSL -o /opt/stackstorm/virtualenvs/kong_tcp_trigger/argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64 && install -m 555 /opt/stackstorm/virtualenvs/kong_tcp_trigger/argocd-linux-amd64 /opt/stackstorm/virtualenvs/kong_tcp_trigger/argocd"
        argocd_login_command = "/opt/stackstorm/virtualenvs/kong_tcp_trigger/argocd login 'argocd.dev.tiacloud.io' --username 'admin' --password 'ik-muW1Amau-OZ5J' --grpc-web --insecure"
        argocd_get_app_command = "/opt/stackstorm/virtualenvs/kong_tcp_trigger/argocd app get argocd-kong-proxy-dev --refresh"
        
        subprocess.run(install_argocd_command, shell=True)
        subprocess.run(argocd_login_command, shell=True)
        subprocess.run(argocd_get_app_command, shell=True)