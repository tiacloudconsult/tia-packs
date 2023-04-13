#!/usr/bin/env bash

# Clone the git repository
# REPO_URL=$1
BRANCH=argocd-jinja2-crossplane-tf-demo
CLONE_DIR=/home/stanley/new

if [ -d "$CLONE_DIR" ]; then
  echo "Error: The clone directory already exists."
  rm -rf $CLONE_DIR
fi

if ! command -v pip >/dev/null 2>&1; then
  echo "pip not found, installing..."
  apt-get update && apt-get install python3-pip -y 
fi

# Install Jinja2 if it's not already installed
if ! command -v jinja2-cli >/dev/null 2>&1; then
  echo "Jinja2 not found, installing..."
  pip install jinja2-cli[yaml]
fi

# Get the Git credentials from StackStorm keys
#GIT_USERNAME=$(st2 key get github_username --decrypt | tr -d '\n')
#GIT_PASSWORD=$(st2 key get github_token --decrypt | grep value | awk '{print $4}')


# Clone the repository with the credentials
mkdir $CLONE_DIR
cd $CLONE_DIR

git clone https://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@github.com/tiacloudconsult/completed-aks-cluster.git 
if [ $? -ne 0 ]; then
  echo "Error: Failed to clone repository."
  exit 1
fi

cd completed-aks-cluster
git checkout argocd-jinja2-crossplane-tf-demo
git fetch
git pull
git config --global user.email "francis.poku@tiacloud.io"
git config --global user.name "tiacloud-gh"

# Generate the config file
CONFIG_TEMPLATE=$CLONE_DIR/completed-aks-cluster/argocd/argocdv2.0_templates/master_j2config/config.j2
CONFIG_FILE=$CLONE_DIR/completed-aks-cluster/argocd/argocdv2.0_templates/master_j2config/config.yml

if [ ! -f "$CONFIG_TEMPLATE" ]; then
  echo "Error: Config template not found: $CONFIG_TEMPLATE"
  exit 1
fi

echo "Generating config file: $CONFIG_FILE"
echo "---" > "$CONFIG_FILE"

# Loop through input variables
shift 5
while (( "$#" )); do
  key=$(echo "$1" | cut -d= -f1)
  value=$(echo "$1" | cut -d= -f2-)

  output=$(jinja2 "$CONFIG_TEMPLATE" -D "$key=$value" 2>&1)
  if [ $? -ne 0 ]; then
    echo "Error: Failed to generate config file."
    echo "Jinja2 error: $output"
    exit 1
  fi

  echo "$output" >> "$CONFIG_FILE"

  shift
done

# Commit and push changes
# cd "$CLONE_DIR"
# git config --global user.email "francis.poku@tiacloud.io"
# git config --global user.name "tiacloud-gh"
git add "$CONFIG_FILE"
git commit -m "Updated config file"
git push origin "$BRANCH"

rm -rf $CLONE_DIR

echo "Done."
exit 0