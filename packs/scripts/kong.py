import os
import yaml
from jinja2 import Template
from git import Repo

# Define the path to the YAML file
yaml_file = "/Users/fpoku/tia/cd-infra/stackstorm/tia-packs/packs/scripts/kong.yaml"

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
port = "3004"  # Replace with your desired port

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

# # Commit changes to the Git repository
# repo = Repo(os.getcwd())
# repo.git.add(yaml_file)
# repo.git.commit("-m", "Added new configuration for Kong")
# repo.git.push()

print("Configuration update complete.")
