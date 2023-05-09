from sms77api.Sms77api import Sms77api

from st2common.runners.base_action import Action


class SevenSendSMSAction(Action):
    def __init__(self, config=None, action_service=None):
        super(SevenSendSMSAction, self).__init__(config, action_service)
        self.client = Sms77api(self.config['api_key'], 'StackStorm')

    def run(self, to, text, **kwargs):
        def on_error(ex):
            error_msg = ('Failed sending sms to: %s, exception: %s\n' % (to, str(ex)))
            self.logger.error(error_msg)
            raise Exception(error_msg)

        kwargs['debug'] = kwargs.pop('sandbox', False)

        try:
            res = self.client.sms(to, text, kwargs)
            if int(res) not in [100, 101]:
                on_error(Exception(res))

        except Exception as e:
            on_error(e)

        self.logger.info('Successfully sent sms to: %s\n' % to)
