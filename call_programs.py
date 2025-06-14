import subprocess
import time
import signal
import os

import serial

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

        line = process.stdout.readline()

        if line:
            l_str = line.strip()

            if l_str != "":
                print(f"KINECT ({i}):", l_str)
                i+=1
        
        # READ POX

        if ser is None:
            continue

        line = ser.readline().decode("utf-8").strip()

        if line:
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