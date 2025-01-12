import psutil
from colorama import Fore, Style


class ThirdPartySoftwareDetector:
    # Define exception words for system apps
    exception_words = ["windows", "system32", "programdata\\microsoft"]

    def __init__(self):
        self.data = []

    def is_system_process(self, process_name, process_exe):
        """
        Determine if the given process is likely a system process.
        """
        system_process_names = [
            "svchost.exe", "explorer.exe", "taskhost.exe", "System Idle Process", "csrss.exe",
            "smss.exe", "winlogon.exe", "services.exe", "lsass.exe"
        ]

        # Normalize path for case-insensitive comparison
        process_exe = (process_exe or "").lower().replace(" ", "")

        # Check if the process name is a common system process name
        if process_name.lower() in (name.lower() for name in system_process_names):
            return True

        # Check if the process executable path contains known system directories
        if (
            process_exe.startswith(r"c:\windows\system32") or
            process_exe.startswith(r"c:\programdata\microsoft") or
            process_exe.startswith(r"c:\windows")
        ):
            return True

        # Check if the path contains any exception words
        if any(word in process_exe for word in self.exception_words):
            return True

        return False

    def fetch_data(self):
        """
        Fetch third-party software and store it as a temporary database.
        """
        process_map = {}

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                process_name = proc.info['name']
                process_exe = proc.info['exe'] or ""
                process_user = proc.info['username']

                # Skip system processes
                if process_name and not self.is_system_process(process_name, process_exe):
                    # Group processes by their executable path
                    if process_exe not in process_map:
                        process_map[process_exe] = {
                            'name': process_name,
                            'user': process_user,
                            'pids': []
                        }
                    process_map[process_exe]['pids'].append(proc.info['pid'])

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Ignore processes that terminate or cannot be accessed
                continue

        # Convert to a structured temporary database
        self.data = []
        for path, details in process_map.items():
            self.data.append({
                'Name': details['name'],
                'User': details['user'],
                'Path': path,
                'PIDs': details['pids'],
                'Multiple_PIDs': len(details['pids']) > 1,
                'None_User': details['user'] is None
            })

        return self.data


