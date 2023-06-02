import os


for yaml_file in ("test.yml", "test2.yml", "test3.yml"):
    # Save the configuration file to disk
    base_dir = 'argocd/apps/'
    file_name = os.path.splitext(yaml_file)[0]
    config_path = os.path.join("/Users/fpoku/tia/cd-infra/stackstorm/tia-packs", base_dir, file_name, yaml_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    print(config_path)