import requests

# Argo CD API configuration
argocd_server = "argocd.dev.tiacloud.io"
argocd_username = "admin"
argocd_password = "ik-muW1Amau-OZ5J"

# Login to Argo CD
login_url = f"https://{argocd_server}/api/v1/session"
login_data = {"username": argocd_username, "password": argocd_password}
response = requests.post(login_url, json=login_data, verify=False)

if response.status_code == 200:
    print("Login successful.")
else:
    print("Login failed.")
    exit(1)

# Get the application details
application_name = "st2-pack-install-cm-dev"
app_url = f"https://{argocd_server}/api/v1/applications/{application_name}"
app_response = requests.get(app_url, cookies=response.cookies, verify=False)

if app_response.status_code == 200:
    print(f"Application '{application_name}' details retrieved successfully.")
else:
    print(f"Failed to retrieve application '{application_name}' details.")
    exit(1)

# Refresh the application
refresh_url = f"https://{argocd_server}/api/v1/applications/{application_name}/actions/sync"
refresh_response = requests.post(refresh_url, cookies=response.cookies, verify=False)

if refresh_response.status_code == 200:
    print(f"Application '{application_name}' refreshed successfully.")
else:
    print(f"Failed to refresh application '{application_name}'.")
    exit(1)