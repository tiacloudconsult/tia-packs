from sms77api.Sms77api import Sms77api

from st2common.runners.base_action import Action


class SevenSendVoiceAction(Action):
    def __init__(self, config=None, action_service=None):
        super(SevenSendVoiceAction, self).__init__(config, action_service)
        self.client = Sms77api(self.config['api_key'], 'StackStorm')

    def run(self, to, text, **kwargs):
        def on_error(ex):
            error_msg = ('Failed sending voice to: %s, exception: %s\n' % (to, str(ex)))
            self.logger.error(error_msg)
            raise Exception(error_msg)

        try:
            res = self.client.voice(
                to, text, kwargs.get('xml', False), kwargs.get('from', None))
            lines = res.splitlines()
            code = lines[0]
            if 100 != int(code):
                on_error(Exception(code))

        except Exception as e:
            on_error(e)

        self.logger.info('Successfully sent voice to: %s\n' % to)
