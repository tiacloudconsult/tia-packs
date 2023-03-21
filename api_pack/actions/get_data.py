import requests
from st2common.runners.base_action import Action

class GetDataAction(Action):
    def run(self, api_url, endpoint):
        url = f"http://{api_url}/{endpoint}"
        response = requests.get(url)
        return response.json()
