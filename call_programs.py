import subprocess
import time
import signal
import os

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
    while True:
        i=0
        for line in process.stdout:
            print(f"Received ({i}):", line.strip())
            i+=1
        time.sleep(0.2)

except KeyboardInterrupt:
    # Send CTRL_BREAK_EVENT (can only be sent to process groups)
    process.send_signal(signal.CTRL_BREAK_EVENT)

    for line in process.stdout:
        print("Received (end):", line.strip())

    print('Interrupted')
