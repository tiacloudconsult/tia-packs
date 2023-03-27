

```sh
# PAT
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

# Install other dependencies
st2 run packs.install packs=python
st2 run packs.install packs=rabbitmq
st2 run packs.install packs=email

```

# ST2
```sh
# Add github token for https clone/pull
st2 key set github_token (YOUR_GITHUB_TOKEN) --encrypt
st2 key list

# Clone private repo
git clone https://<PAT>@github.com/<your-account>/<repo>.git
git clone https://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@github.com/tiacloudconsult/tia-packs.git

# Add git PAT
st2ctl reload --register-configs

# Edit ~/.st2/config
apt-get update
apt-get install vim
vim ~/.st2/config

# Add the following 
git_username: sharhanalhassan
git_password: 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
```

# Rabbit Conf
```sh
# Configure
rabbitmqadmin declare exchange name=demo type=topic durable=false -H mm-rabbit-rabbitmq-0.mm-rabbit-rabbitmq-headless.rabbit.svc.cluster.local -P 15672 -u test -p test

rabbitmqadmin declare queue name=demoqueue -H mm-rabbit-rabbitmq-0.mm-rabbit-rabbitmq-headless.rabbit.svc.cluster.local -P 15672 -u test -p test

rabbitmqadmin declare binding source=demo destination=demoqueue routing_key=demokey -H mm-rabbit-rabbitmq-0.mm-rabbit-rabbitmq-headless.rabbit.svc.cluster.local -P 15672 -u test -p test
```

# Errors
```sh

        [ succeeded ] init_task
        [  failed   ] download_pack

id: 6419e7fd73e3c23c8ece3d41
action.ref: packs.install
parameters: 
  packs:
  - api_pack
status: failed
start_timestamp: Tue, 21 Mar 2023 17:23:09 UTC
end_timestamp: Tue, 21 Mar 2023 17:23:30 UTC
log: 
  - status: requested
    timestamp: '2023-03-21T17:23:09.869000Z'
  - status: scheduled
    timestamp: '2023-03-21T17:23:10.411000Z'
  - status: running
    timestamp: '2023-03-21T17:23:11.061000Z'
  - status: failed
    timestamp: '2023-03-21T17:23:30.853000Z'
result: 
  errors:
  - message: Execution failed. See result for details.
    result:
      exit_code: 1
      result: None
      stderr: "Traceback (most recent call last):
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/python_runner/python_action_wrapper.py", line 395, in <module>
    obj.run()
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/python_runner/python_action_wrapper.py", line 214, in run
    output = action.run(**self._parameters)
  File "/opt/stackstorm/packs/packs/actions/pack_mgmt/download.py", line 106, in run
    return self._validate_result(result=result, repo_url=pack_url)
  File "/opt/stackstorm/packs/packs/actions/pack_mgmt/download.py", line 129, in _validate_result
    raise Exception(message)
Exception: The pack has not been downloaded from "None".

Errors:
No record of the "api_pack" pack in the index.
"
      stdout: ''
    task_id: download_pack
    type: error
  output:
    conflict_list: null
    message: ''
    packs_list: null
    warning_list: null
+--------------------------+------------------------+---------------+----------------+-----------------+
| id                       | status                 | task          | action         | start_timestamp |
+--------------------------+------------------------+---------------+----------------+-----------------+
| 6419e80223402fece2388c67 | succeeded (2s elapsed) | init_task     | core.noop      | Tue, 21 Mar     |
|                          |                        |               |                | 2023 17:23:14   |
|                          |                        |               |                | UTC             |
| 6419e80823402fece2388c77 | failed (8s elapsed)    | download_pack | packs.download | Tue, 21 Mar     |
|                          |                        |               |                | 2023 17:23:20   |
|                          |                        |               |                | UTC             |
+--------------------------+------------------------+---------------+----------------+-----------------+







 Pack "api_pack" contains a deprecated config.yaml file (/opt/stackstorm/packs/api_pack/config.yaml). Support for "config.yaml" files has been deprecated in StackStorm v1.6.0 in favor of config.schema.yaml config schema files and config files in /opt/stackstorm/configs/ directory. Support for config.yaml files has been removed in the release (v2.4.0) so please migrate. For more information please refer to https://docs.stackstorm.com/reference/pack_configs.html 
2023-03-21 17:25:59,484 INFO [-] Registered 0 triggers.
2023-03-21 17:25:59,484 INFO [-] =========================================================
2023-03-21 17:25:59,484 INFO [-] ############## Registering sensors ######################
2023-03-21 17:25:59,484 INFO [-] =========================================================
2023-03-21 17:25:59,487 WARNING [-] Failed to register sensors: Failed to register sensor "/opt/stackstorm/packs/api_pack/sensors/get_data_sensor.yaml" from pack "api_pack": Sensor definition missing entry_point
Traceback (most recent call last):
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 130, in _register_sensors_from_pack
    _, altered = self._register_sensor_from_pack(pack=pack, sensor=sensor)
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 169, in _register_sensor_from_pack
    raise ValueError("Sensor definition missing entry_point")
ValueError: Sensor definition missing entry_point

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/bin/st2-register-content", line 22, in <module>
    sys.exit(content_loader.main(sys.argv[1:]))
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/content/bootstrap.py", line 458, in main
    register_content()
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/content/bootstrap.py", line 398, in register_content
    register_sensors()
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/content/bootstrap.py", line 211, in register_sensors
    raise e
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/content/bootstrap.py", line 203, in register_sensors
    (registered_count, overridden_count) = sensors_registrar.register_sensors(
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 228, in register_sensors
    result = registrar.register_from_packs(base_dirs=packs_base_paths)
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 72, in register_from_packs
    raise e
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 65, in register_from_packs
    count, overridden = self._register_sensors_from_pack(
  File "/opt/stackstorm/st2/lib/python3.8/site-packages/st2common/bootstrap/sensorsregistrar.py", line 140, in _register_sensors_from_pack
    raise ValueError(msg)
ValueError: Failed to register sensor "/opt/stackstorm/packs/api_pack/sensors/get_data_sensor.yaml" from pack "api_pack": Sensor definition missing entry_point
```


git_url: "https://github.com/tiacloudconsult/tia-packs.git"
git_branch: "main"

st2 run gitclone.clone_and_list git_url=<git_url> git_branch=<git_branch>

st2 execution get <ID>

# Troubleshooting
```
# Install with file
st2 pack install file:///opt/stackstorm/packs.dev/api_pack


```