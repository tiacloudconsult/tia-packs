

```sh
# PAT
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

# Install other dependencies
st2 run packs.install packs=python
st2 run packs.install packs=rabbitmq
st2 run packs.install packs=email

# St2 run
st2 pack install api_pack --path
st2 run api_pack.get_data
```

# ST2
```sh
# Add github token for https clone/pull
st2 key set github_token (YOUR_GITHUB_TOKEN) --encrypt
st2 key list

# Clone private repo
git clone https://<PAT>@github.com/<your-account>/<repo>.git
git clone https://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@github.com/tiacloudconsult/tia-packs.git

Mohammedtiacloud@2020
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