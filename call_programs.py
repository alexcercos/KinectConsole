import subprocess
import time
import signal
import os
import requests

import serial

def convert_json(values_raw, value_names, error_str="ERROR: WRONG VALUE LENGTH", ts):
    json_obj = {}
    values = values_raw.split(',')

    if len(values)!=len(value_names):
        print(error_str)
        return json_obj

    for i,n in enumerate(value_names):
        json_obj[n] = float(values[i])

    json_obj["timestamp"] = ts

    return json_obj

def convert_json_kinect(values_raw, value_names, error_str="ERROR: WRONG VALUE LENGTH", ts):
    json_obj = {}
    values = values_raw.split(',')

    if len(values)!=len(value_names)*3:
        print(error_str)
        return json_obj

    for i,n in enumerate(value_names):
        json_obj[n] = {
            "x": float(values[i*3]),
            "y": float(values[i*3+1]),
            "z": float(values[i*3+2]),
        }
    json_obj["timestamp"] = ts

    return json_obj

pox_names = ["total_phase","breath_phase","heart_phase","breath_rate","heart_rate","distance"]
kinect_names = [
    "spine_base", "spine_mid", "neck", "head",
    "shoulder_left","elbow_left","wrist_left","hand_left",
    "shoulder_right","elbow_right","wrist_right","hand_right",
    "hip_left","knee_left","ankle_left","foot_left",
    "hip_right","knee_right","ankle_right","foot_right"
]
SERIAL_PORT = "COM5"
BAUD_RATE = 115200

# Windows-specific flags
CREATE_NEW_PROCESS_GROUP = 0x00000200

# Start process in its own process group
process = subprocess.Popen(
    ["C:/Users/Alejandro/Documents/master/IOT/Final/KinectConsole/KinectConsole/bin/Release/KinectConsole.exe"],
    creationflags=CREATE_NEW_PROCESS_GROUP,
    stdout=subprocess.PIPE,
    text=True,            # Decode bytes to strings
    bufsize=1             # Line-buffered
)

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Opened serial connection")
except serial.SerialException:
    print(f"Could not open serial port {SERIAL_PORT}. Check connection")
    ser = None

try:
    print("START",ser is None)
    i=0
    while True:
        
        # READ KINECT
        time_val = time.time()

        line = process.stdout.readline()

        if line:
            l_str = line.strip()

            #Make json
            json_obj = convert_json(l_str, kinect_names, "ERROR: WRONG KINECT VALUE LENGTH",time_val)


            if l_str != "":
                print(f"KINECT ({i}):", l_str)
                i+=1
        
        # READ POX

        if ser is None:
            continue

        line = ser.readline().decode("utf-8").strip()

        if line:

            json_obj = convert_json(line, pox_names, "ERROR: WRONG POX VALUE LENGTH",time_val)
            

            print(f"POX ({i}):",line)
            i+=1


except KeyboardInterrupt:
    print('Interrupted')

finally:

    # Send CTRL_BREAK_EVENT (can only be sent to process groups)
    process.send_signal(signal.CTRL_BREAK_EVENT)

    for line in process.stdout:
        print("Received (end):", line.strip())

    if ser is not None and ser.is_open:
        ser.close()
        print("Serial connection closed")