import subprocess
import os
import yaml
from yaml.loader import SafeLoader

from st2common.runners.base_action import Action

class HelmPackage(Action):
    def run(self):

try:

    # Get the current working directory
    current_dir = os.getcwd()

    # Move two levels up from the current directory
    parent_dir = os.path.dirname(os.path.dirname(current_dir))

    # Specify the directory path inside the parent directory
    target_dir = os.path.join(parent_dir, 'setupst2_docker_vmount', 'k8s')

    # Specify the destination directory for the packaged Helm chart
    output_dir = os.path.join(parent_dir, 'setupst2_docker_vmount', 'k8s','charts')

    # Change the current working directory to the target directory
    os.chdir(target_dir)

    # Define the command to package the Helm chart with the specified output directory
    helm_package_cmd = ['helm', 'package', '.', '--destination', output_dir]

    # Run the command using subprocess
    subprocess.run(helm_package_cmd, check=True)

    print("Helm chart packaging completed.")
except Exception as e:
    print(f'An error occurred; {e}')








