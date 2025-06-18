import time
import requests
import pickle

backend_url = "http://127.0.0.1:5000"

def get_exercise():
    return "biceps_right"

with open('exercise.pkl', "rb") as input_file:
    complete_data = pickle.load(input_file)

exercise = get_exercise()

while exercise is None: #Wait for exercise start (API)
    time.sleep(0.5)
    exercise = get_exercise()

for entry in complete_data:
    data_type, data_dict = entry

    if data_type == "pox":
        print("P:",data_dict)
        requests.post(f"{backend_url}/sendPox", json=data_dict)
    else:
        print("K;",data_dict)
        requests.post(f"{backend_url}/sendKinect", json=data_dict)

    exercise = get_exercise()
    time.sleep(0.1) #arbitrary time

