import requests
import subprocess
import time

def trigger_webhook(username):
    url = 'http://127.0.0.1:82/api/v1/webhooks/argocd_trigger'
    headers = {
        'Content-Type': 'application/json',
        'St2-Api-Key': 'ZmY5ZjRlYjMyZTZlY2VlOWZkOTc3ODZkM2M3NTFlOTBiOWY1NTQ1YmY2OGNkYzg5Yzk0MTA2ZDMwMGRkYjU4MA',
    }
    payload = {
        "git_branch": "dev",
        "config_template": "config.j2",
        "config_file": "config.yml",
        "yaml_template": "tiacourses.j2, tiacourses_hpa_config.j2",
        "yaml_file": f"tiacourses.{username}.yaml, tiacourses.{username}.hpa.yaml",
        "argocdApp_template": "argocd_deploy_config.j2",
        "argocdApp_file": "argocd-tiacourses-dev.yaml",
        "input_vars": {
            "environment": "tiacourses-dev",
            "project": "dev",
            "port": f"{port}"
            "username": username,
            "server": "https://aks-dns-vs966uez.hcp.eastus.azmk8s.io:443",
            "AppPath": "tiacourses"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 202:
        print("Webhook triggered successfully!")
    else:
        print("Failed to trigger webhook. Status code:", response.status_code)


def get_external_ip():
    command = "kubectl get svc -n tiacourses"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout
        external_ip = parse_external_ip(output)
        return external_ip
    else:
        print("Failed to get external IP. Error:", result.stderr)
        return None

def parse_external_ip(output):
    lines = output.split("\n")
    for line in lines[1:]:
        columns = line.split()
        if len(columns) > 3 and columns[0] == "tiacourses":
            external_ip = columns[3]
            return external_ip
    return None

def check_cluster_access():
    command = "kubectl get nodes"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        print("Failed to access the AKS cluster. Error:", result.stderr)
        return False

def wait_for_resources(timeout):
    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < timeout:
        if check_cluster_access():
            external_ip = get_external_ip()
            if external_ip:
                return external_ip
        
        print("Waiting for resources to be generated...")
        time.sleep(5)
        elapsed_time = time.time() - start_time

    print(f"Timeout reached. Waited for {elapsed_time:.2f} seconds.")

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Add your authentication logic here
    # For example, you can compare the username and password with a database or hardcoded values

    # Assuming authentication is successful, trigger the webhook
    trigger_webhook(username)

    # Wait for the resources to be generated with a timeout of 7 minutes (420 seconds)
    wait_for_resources(420)

    print("Welcome to tiacourses! Run the following command on your terminal to start:")
    print(f"ssh vagrant@{get_external_ip}")

login()