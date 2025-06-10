import subprocess
import time
import signal
import os

# Windows-specific flags
CREATE_NEW_PROCESS_GROUP = 0x00000200

# Start process in its own process group
process = subprocess.Popen(
    ["C:/Users/Alejandro/Documents/master/IOT/Final/KinectConsole/KinectConsole/bin/Release/KinectConsole.exe"],
    creationflags=CREATE_NEW_PROCESS_GROUP
)

time.sleep(5)

# Send CTRL_BREAK_EVENT (can only be sent to process groups)
process.send_signal(signal.CTRL_BREAK_EVENT)