import subprocess
import time
import signal
import os
import requests
import math

import serial

import open3d as o3d

def vector_from_to(a, b):
    """Returns the vector from point a to point b."""
    return [b['x'] - a['x'], b['y'] - a['y'], b['z'] - a['z']]

def vector_angle(v1, v2):
    """Calculates the angle in degrees between two 3D vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    
    if mag1 == 0 or mag2 == 0:
        return 0  # Cannot compute angle with zero-length vector
    
    cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))  # Clamp to avoid floating-point errors
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)

def convert_json(values_raw, value_names, error_str, ts):
    json_obj = {}
    values = values_raw.split(',')

    if len(values)!=len(value_names):
        print(error_str)
        return json_obj

    for i,n in enumerate(value_names):
        json_obj[n] = float(values[i])

    json_obj["timestamp"] = ts

    return json_obj

def convert_json_kinect(values_raw, value_names, error_str):
    json_obj = {}
    values = values_raw.split(',')

    if len(values)!=len(value_names)*3:
        print(error_str,len(values),len(value_names)*3)
        return json_obj

    for i,n in enumerate(value_names):
        json_obj[n] = {
            "x": float(values[i*3]),
            "y": float(values[i*3+1]),
            "z": float(values[i*3+2]),
        }

    return json_obj

def create_initial_dict(value_names):
    json_obj = {}

    for n in value_names:
        json_obj[n] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

    return json_obj

def get_exercise():
    return "biceps_right"

def calculate_metrics(skeleton_json, config):
    mid_joint = config["mid_joint"]
    moving_joint = config["moving_joint"]
    end_joint = config["end_joint"]
    start_angle = config["start_angle"]
    end_angle = config["end_angle"]

    # Get positions
    mid = skeleton_json[mid_joint]
    moving = skeleton_json[moving_joint]
    end = skeleton_json[end_joint]

    # Vectors
    vec1 = vector_from_to(mid, end)
    vec2 = vector_from_to(mid, moving)

    # Compute angle
    angle = vector_angle(vec1, vec2)

    # Normalize angle to completeness percentage
    angle_range = start_angle - end_angle
    if angle_range == 0:
        completeness = 0.0  # Avoid division by zero
    else:
        completeness = (start_angle - angle) / angle_range * 100
        completeness = max(0.0, min(100.0, completeness))  # Clamp to 0-100%

    # Update JSON
    skeleton_json["completeness"] = completeness

pox_names = ["total_phase","breath_phase","heart_phase","breath_rate","heart_rate","distance"]
kinect_names = [
    "spine_base", "spine_mid", "neck", "head",
    "shoulder_left","elbow_left","wrist_left","hand_left",
    "shoulder_right","elbow_right","wrist_right","hand_right",
    "hip_left","knee_left","ankle_left","foot_left",
    "hip_right","knee_right","ankle_right","foot_right",
    "spine_shoulder"
]

kinect_connections = [
    ("head", "neck"),("neck", "spine_shoulder"),("spine_shoulder","spine_mid"),("spine_mid","spine_base"),
    ("spine_shoulder","shoulder_left"),("shoulder_left","elbow_left"),("elbow_left","wrist_left"),("wrist_left","hand_left"),
    ("spine_shoulder","shoulder_right"),("shoulder_right","elbow_right"),("elbow_right","wrist_right"),("wrist_right","hand_right"),
    ("spine_base","hip_left"),("hip_left","knee_left"),("knee_left","ankle_left"),("ankle_left","foot_left"),
    ("spine_base","hip_right"),("hip_right","knee_right"),("knee_right","ankle_right"),("ankle_right","foot_right")
]

exercises = {
    "biceps_right": {
        "mid_joint": "elbow_right",
        "moving_joint": "wrist_right",
        "end_joint": "shoulder_right",
        "exclude": ["hand_right"],
        "start_angle": 180,
        "end_angle": 0,
    },
    "biceps_left": {
        "mid_joint": "elbow_left",
        "moving_joint": "wrist_left",
        "end_joint": "shoulder_left",
        "exclude": ["hand_left"],
        "start_angle": 180,
        "end_angle": 0,
    },
    "quad_right": {
        "mid_joint": "knee_right",
        "moving_joint": "ankle_right",
        "end_joint": "hip_right",
        "exclude": ["foot_right"],
        "start_angle": 90,
        "end_angle": 180,
    },
    "quad_left": {
        "mid_joint": "knee_left",
        "moving_joint": "ankle_left",
        "end_joint": "hip_left",
        "exclude": ["foot_left"],
        "start_angle": 90,
        "end_angle": 180,
    },
    "triceps_right": {
        "mid_joint": "elbow_right",
        "moving_joint": "wrist_right",
        "end_joint": "shoulder_right",
        "exclude": ["hand_right"],
        "start_angle": 0,
        "end_angle": 180,
    },
    "triceps_left": {
        "mid_joint": "elbow_left",
        "moving_joint": "wrist_left",
        "end_joint": "shoulder_left",
        "exclude": ["hand_left"],
        "start_angle": 0,
        "end_angle": 180,
    }
}


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

debug_lines = True
vis = None

exercise = None
line_set = None
pcd = None

try:
    i=0
    running = False

    if debug_lines:
        vis = o3d.visualization.Visualizer()
        vis.create_window()

        kinect_json = create_initial_dict(kinect_names)
        points = [[v["x"], v["y"], v["z"]] for v in kinect_json.values()]
        lines = [[list(kinect_json.keys()).index(a), list(kinect_json.keys()).index(b)] for a, b in kinect_connections]
        
        line_set = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(points),
            lines=o3d.utility.Vector2iVector(lines),
        )
        vis.add_geometry(line_set)

        coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)
        vis.add_geometry(coord_frame)

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.paint_uniform_color([0, 1, 0])  # Green points

        vis.add_geometry(pcd)

    while True:
        
        exercise = get_exercise()

        if exercise is None:
            time.sleep(0.5)
            continue

        # READ KINECT
        time_val = time.time()

        line = process.stdout.readline().strip()

        if line != "":

            #Make json
            kinect_json = convert_json_kinect(line, kinect_names, "ERROR: WRONG KINECT VALUE LENGTH")

            if debug_lines:
                points = [[v["x"], v["y"], v["z"]] for v in kinect_json.values()]
                line_set.points = o3d.utility.Vector3dVector(points)
                pcd.points = o3d.utility.Vector3dVector(points)
                vis.update_geometry(line_set)
                vis.update_geometry(pcd)
                vis.poll_events()
                vis.update_renderer()

            kinect_json["timestamp"] = time_val

            calculate_metrics(kinect_json, exercises[exercise])


            #print(f"KINECT ({i}):", line)
            print(kinect_json["completeness"])
            i+=1
        elif debug_lines:
            vis.poll_events()
            vis.update_renderer()
        
        # READ POX

        if ser is None:
            continue

        line = ser.readline().decode("utf-8").strip()

        if line != "":

            json_obj = convert_json(line, pox_names, "ERROR: WRONG POX VALUE LENGTH",time_val)
            

            print(f"POX ({i}):",line)
            i+=1


except KeyboardInterrupt:
    print('Interrupted')

finally:

    if debug_lines:
        vis.destroy_window()

    # Send CTRL_BREAK_EVENT (can only be sent to process groups)
    process.send_signal(signal.CTRL_BREAK_EVENT)

    for line in process.stdout:
        print("Received (end):", line.strip())

    if ser is not None and ser.is_open:
        ser.close()
        print("Serial connection closed")