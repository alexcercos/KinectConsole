import time
import requests
import pickle

exercises_names = [
    "biceps_right",
    "biceps_left",
    "quad_right",
    "quad_left",
    "triceps_right",
    "triceps_left",
    None
]

backend_url = "http://127.0.0.1:5000"

def get_exercise():
    exercise_resp = requests.get(f"{backend_url}/getCurrentExercise",json={"user_id": 0}, timeout=1)
    
    json_resp = exercise_resp.json()
    print("Exercise:",exercises_names[json_resp["current_exercise"]],json_resp["current_exercise"])
    return exercises_names[json_resp["current_exercise"]]

with open('exercise.pkl', "rb") as input_file:
    complete_data = pickle.load(input_file)

# deberia hacerse en frontend

#createSession
#addExercise
resp = requests.post(f"{backend_url}/setCurrentExercise", json={"user_id": 0, "exercise": 0}, timeout=1)

#requests.post(f"{backend_url}/createExercise")
print(resp.text)

exercise = get_exercise()

while exercise is None: #Wait for exercise start (API)
    time.sleep(0.5)
    exercise = get_exercise()

for entry in complete_data:
    data_type, data_dict = entry

    if data_type == "pox":
        print("P:",data_dict)
        requests.post(f"{backend_url}/sendPox", json=data_dict)
        #TODO add exercise_id to jsons
    else:
        print("K;",data_dict)
        for k, v in data_dict.items():
            if isinstance(v, dict): data_dict[k] = str(v)
        requests.post(f"{backend_url}/sendKinect", json=data_dict)
        #TODO add exercise_id to jsons

    exercise = get_exercise()

    if exercise is None:
        break

    time.sleep(0.1) #arbitrary time

#TODO
#setMetrics
