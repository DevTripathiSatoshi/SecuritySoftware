import customtkinter as ctk
from threading import Thread, Lock
import time
from ctypes import windll, c_void_p
import psutil
import cv2
from pycaw.pycaw import AudioUtilities, IAudioSessionManager2
from pycaw.constants import AudioSessionState
from ctypes import POINTER, c_int, c_ulong


#
#  Main 
#
#


name = "Mic & Camera Indicator"
on_text = "Enabled"
off_text = "Disabled"
is_on = False







# Boolean flags to control the display of dots
mic_in_use = False
cam_in_use = False
screen_recording_in_use = False  # New flag for screen recording
flags_lock = Lock()  # Lock for thread safety


class OverlayDot:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'white')
        self.root.overrideredirect(True)
        self.root.geometry(f"150x100+{self.get_screen_width() - 150}+0")
        self.root.configure(fg_color="white")  # For transparency

        self.canvas = ctk.CTkCanvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True)
        self.running = True

    def get_screen_width(self):
        user32 = windll.user32
        return user32.GetSystemMetrics(0)

    def update_dots(self):
        """
        Update the dots based on the global boolean flags.
        """
        global mic_in_use, cam_in_use, screen_recording_in_use
        self.canvas.delete("all")
        x_offset = 10

        with flags_lock:
            if mic_in_use:
                # Green dot for microphone
                self.canvas.create_oval(x_offset, 10, x_offset + 30, 10, fill="green", outline="")
                x_offset += 40

            if cam_in_use:
                # Red dot for camera
                self.canvas.create_oval(x_offset, 10, x_offset + 30, 10, fill="red", outline="")
                x_offset += 40

            if screen_recording_in_use:
                # Yellow dot for screen recording
                self.canvas.create_oval(x_offset, 10, x_offset + 30, 10, fill="yellow", outline="")

        self.root.update()

    def run(self):
        """
        Main loop for the Tkinter application.
        """
        def periodic_update():
            while self.running:
                self.update_dots()
                time.sleep(1)

        # Start a background thread to periodically update the dots
        update_thread = Thread(target=periodic_update, daemon=True)
        update_thread.start()

        self.root.mainloop()

    def stop(self):
        """
        Stop the application gracefully.
        """
        self.running = False
        self.root.quit()


def get_audio_applications():
    """
    Get a list of applications currently using the audio input/output.
    """
    # Initialize COM library for pycaw
    from ctypes import windll
    windll.ole32.CoInitialize(None)  # Initialize COM

    sessions = AudioUtilities.GetAllSessions()
    apps = []
    for session in sessions:
        if session.Process:
            apps.append(session.Process)
    
    windll.ole32.CoUninitialize()  # Uninitialize COM
    return apps


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


def check_camera_and_mic_usage():
    """
    Periodically check if any software is using the camera or microphone.
    Update the global flags accordingly.
    """
    global mic_in_use, cam_in_use

    while True:
        with flags_lock:
            mic_in_use = False
            cam_in_use = False

            # Check for audio applications
            audio_apps = get_audio_applications()
            for app in audio_apps:
                app_name = app.name().lower()  # Access process name directly
                if app_name in ['zoom.exe', 'teams.exe', 'skype.exe', 'discord.exe']:
                    mic_in_use = True

            # Check for camera usage
            cam_in_use = is_camera_in_use()

        time.sleep(5)  # Periodically check every 5 seconds


def simulate_flag_changes():
    """
    Simulates changes to the mic_in_use, cam_in_use, and screen_recording_in_use flags for demonstration.
    """
    global mic_in_use, cam_in_use, screen_recording_in_use
    while True:
        time.sleep(5)
            





#
#
#
#
#

overlay = OverlayDot() 

def onEnable():
    

    # Start a background thread to monitor camera and microphone usage
    mic_cam_check_thread = Thread(target=check_camera_and_mic_usage, daemon=True)
    mic_cam_check_thread.start()

    # Start a background thread to simulate changes in flags (for demonstration)
    flag_simulation_thread = Thread(target=simulate_flag_changes, daemon=True)
    flag_simulation_thread.start()
    global is_on
    is_on = True

    # Run the overlay
    overlay.run()
    


def onDisable():
    global is_on
    is_on = False

    # Start a background thread to monitor camera and microphone usage
    mic_cam_check_thread = Thread(target=check_camera_and_mic_usage, daemon=True)
    mic_cam_check_thread.start()

    # Start a background thread to simulate changes in flags (for demonstration)
    flag_simulation_thread = Thread(target=simulate_flag_changes, daemon=True)
    flag_simulation_thread.start()

    
    overlay.stop()
    

