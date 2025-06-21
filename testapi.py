import requests
from endpoint import backend_url

# r = requests.get(backend_url+"/sets?session_id=1",json={"":""})
r = requests.get(backend_url+"/getExercise?exercise_id=1",json={"":""})
print(r.text)
