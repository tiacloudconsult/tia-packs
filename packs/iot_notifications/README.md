![](https://www.seven.io/wp-content/uploads/Logo.svg "seven Logo")

# seven Integration Pack

This StackStorm pack allows integration with [seven](https://www.seven.io/) service.

## Installation

`st2 pack install https://github.com/seven-io/StackStorm`

## Configuration

Copy [seven.yaml.dist](seven.yaml.dist) to `/opt/stackstorm/configs/seven.yaml` and edit
it as required.

- ``api_key`` - Your API key - get it in
  the [developer dashboard](https://app.seven.io/developer).

Dynamic values from the datastore can be used too -
see [documentation](https://docs.stackstorm.com/reference/pack_configs.html).

**Caution** : Remember to tell StackStorm to reload new values after modifying the
configuration in `/opt/stackstorm/configs/` by running `st2ctl reload --register-configs`

## Actions

- **send_sms** - Action which sends SMS. Multiple recipients can be separated by comma.
  `st2 run seven.send_sms to="01716992343,491625453093" text=HI2U from=StackStorm flash=true performance_tracking=true sandbox=false no_reload=true label=CustomLabel foreign_id=ForeignID delay="2021-12-30 12:00"`

- **send_voice** - Action which makes a text-to-speech call using seven API.
  `st2 run seven.send_voice to=+491716992343 text='Dear sir or madam' from=+13134378004 xml=false`

### Support

Need help? Feel free to [contact us](https://www.seven.io/en/company/contact/).

[![MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)