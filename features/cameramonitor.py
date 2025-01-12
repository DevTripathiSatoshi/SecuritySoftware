import psutil
import cv2
import time
import json
from datetime import datetime
import threading
from comtypes import CoInitialize, CoUninitialize

monitor_thread = None  # To keep track of the monitoring thread
stop_monitoring = threading.Event()  # Event to signal thread termination

LOG_FILE = "camera_access_logs.json"
is_on = False
  
def onEnable():
    global is_on, monitor_thread
    if not is_on:
        is_on = True
        stop_monitoring.clear()
        monitor_thread = threading.Thread(target=monitor_camera, daemon=True)
        monitor_thread.start()

def onDisable():
    global is_on
    if is_on:
        stop_monitoring.set()
        is_on = False

def logs(data):
    """
    Save log data to a JSON file.
    """
    try:
        with open(LOG_FILE, "r") as file:
            log_data = json.load(file)
    except FileNotFoundError:
        log_data = []

    log_data.append(data)
    with open(LOG_FILE, "w") as file:
        json.dump(log_data, file, indent=4)

def close_application_by_pid(pid):
    """
    Close an application by its PID.
    """
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        print(f"[WARNING] Closing process: {process_name} (PID: {pid})")
        process.terminate()
        return process_name, pid
    except psutil.NoSuchProcess:
        return None, None

def is_camera_in_use():
    """
    Check if the camera is in use by trying to open it.
    """
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            return True
    except Exception:
        pass
    return False

def monitor_camera():
    """
    Monitor applications using the camera and terminate them.
    """
    CoInitialize()
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "Started Monitoring Camera Access",
        }
        logs(log_entry)
        while not stop_monitoring.is_set():
            if is_camera_in_use():
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        # Additional filtering logic can be added here
                        name, pid = close_application_by_pid(proc.info['pid'])
                        if name and pid:
                            log_entry = {
                                "timestamp": datetime.now().isoformat(),
                                "action": "Blocked",
                                "process_name": name,
                                "process_id": pid,
                            }
                            logs(log_entry)
                    except Exception as e:
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "action": f"[Error] {e}",
                        }
                        logs(log_entry)
            time.sleep(1)
    finally:
        CoUninitialize()
