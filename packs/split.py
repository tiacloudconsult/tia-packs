import os


for yaml_file in ("test.namespace.yml", "test2.namespace.yml", "test3.namespace.yml"):
    # Save the configuration file to disk
    base_dir = 'argocd/apps/'
    file_name = os.path.splitext(yaml_file)[0]
    config_path = os.path.join("/Users/fpoku/tia/cd-infra/stackstorm/tia-packs", base_dir, file_name, yaml_file)
    print(config_path)