
import requests

def fetch(url):
  response = requests.get(url)
  return response.json()

url = "https://swapi.dev/api/planets/3/?format=json"

print(fetch(url))