import time
import requests
import pickle

from endpoint import backend_url

def get_exercise():
    exercise_resp = requests.get(f"{backend_url}/getCurrentExercise?user_id=1",json={"":""})
    
    json_resp = exercise_resp.json()
    
    current_id = json_resp["current_exercise"]["exercise"]
    set_id = json_resp["current_exercise"]["set_id"]
    if current_id < 0: return None, None
    
    resp = requests.get(f"{backend_url}/getExercise?exercise_id={current_id}",json={"":""})

    json_name = resp.json()

    return json_name["name"], set_id

exercises_names = [
    "biceps_right",
    "biceps_left",
    "quad_right",
    "quad_left",
    "triceps_right",
    "triceps_left",
    None
]

with open('exercise.pkl', "rb") as input_file:
    complete_data = pickle.load(input_file)


exercise, set_id = get_exercise()

while exercise is None: #Wait for exercise start (API)
    time.sleep(0.5)
    exercise, set_id = get_exercise()

for entry in complete_data:
    data_type, data_dict = entry

    if data_type == "pox":
        print("POX",data_dict["timestamp"])
        data_dict["set_id"] = set_id
        requests.post(f"{backend_url}/sendPox", json=data_dict)

    else:
        print("KINECT",data_dict["timestamp"])
        for k, v in data_dict.items():
            if isinstance(v, dict): data_dict[k] = str(v)
        data_dict["set_id"] = set_id
        requests.post(f"{backend_url}/sendKinect", json=data_dict)

    exercise,set_id = get_exercise()

    if exercise is None:
        break

    time.sleep(0.1) #arbitrary time
