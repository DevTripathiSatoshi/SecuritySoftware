import psutil
from pycaw.pycaw import AudioUtilities
import time
import json
from datetime import datetime
import os 
import threading
from comtypes import CoInitialize, CoUninitialize





monitor_thread = None  # To keep track of the monitoring thread
stop_monitoring = threading.Event()  # Event to signal thread termination


#
#
#                     Cogs Code
#
#
#


name = "Super Mute"
on_text = "Enabled"
off_text = "Disabled"
is_on = False


def onEnable():
    global is_on, monitor_thread
    if not is_on:
        is_on = True
        stop_monitoring.clear()
        monitor_thread = threading.Thread(target=monitor_microphone, daemon=True)
        monitor_thread.start()
    


def onDisable():
    global is_on
    if is_on:
        stop_monitoring.set()
        is_on = False
    


#
#
#
#             Working Code 
#
#

LOG_FILE = "microphone_access_logs.json"

def get_audio_applications():
    """
    Get a list of applications currently using the audio input/output.
    """
    sessions = AudioUtilities.GetAllSessions()
    apps = []
    for session in sessions:
        if session.Process:
            apps.append(session.Process)
    return apps

def close_application(process_name):
    """
    Close an application by name.
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                print(f"[WARNING] Closing process: {proc.info['name']} (PID: {proc.pid})")
                proc.terminate()
                return proc.info['name'], proc.pid
        except psutil.NoSuchProcess:
            pass
    return None, None


#
#
#          Logs 
#
#
#

def logs(data):
    """
    Save log data to a JSON file.
    """
    try:
        # Read existing logs
        with open(LOG_FILE, "r") as file:
            log_data = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, initialize log_data
        log_data = []

    # Append new data
    log_data.append(data)

    # Write back to file
    with open(LOG_FILE, "w") as file:
        json.dump(log_data, file, indent=4)


#
#
#
#       Logs End
#
#

def monitor_microphone():
    """
    Monitor applications using the microphone and log their details.
    """
    CoInitialize()  # Initialize COM in the thread
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "Established Monitoring Microphone Access",
        }
        logs(log_entry)
        blocked_apps = set()
        while not stop_monitoring.is_set():
            try:
                apps = get_audio_applications()
                for app in apps:
                    process_name = app.name()
                    if process_name not in blocked_apps:
                        blocked_apps.add(process_name)
                    name, pid = close_application(process_name)
                    if name and pid:
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "action": "Blocked",
                            "process_name": name,
                            "process_id": pid,
                        }
                        logs(log_entry)
                time.sleep(1)
            except Exception as e:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": f"[Error] {e}",
                }
                logs(log_entry)
    finally:
        CoUninitialize()  # Clean up COM when the thread exits




