import requests
import yaml
from types import SimpleNamespace


url = 'http://localhost:8080'


resp = requests.get(url=url)
data = resp.json() # Check the JSON Response Content documentation below

file = open("output_file.yaml", "w")
yaml.dump(resp.json(), file)
file.close()

