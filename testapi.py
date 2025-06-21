import requests
from endpoint import backend_url

r = requests.get(backend_url+"/dbGet?table=exercise",json={"":""})
print(r.text)
