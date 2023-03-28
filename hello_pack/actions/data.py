import requests
from st2common.runners.base_action import Action

class GetDataAction(Action):
    def run(self, url):
        response = requests.get(url)
        return response.json()