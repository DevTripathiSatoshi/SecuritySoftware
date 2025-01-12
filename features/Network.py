import customtkinter as ctk
import psutil
import socket
import threading
from tkinter import ttk


name = "Network Monitor"
on_text = "Exit"
off_text = "View"
is_on = False


def onEnable():
    NetworkUsageWindow()


def onDisable():
    NetworkUsageWindow.destroy()  # Gracefully terminate the app


import customtkinter as ctk
import psutil
import socket
import threading
import queue
from tkinter import ttk


class NetworkUsageDetector:
    def __init__(self):
        self.data = []

    def get_connected_urls(self):
        """
        Get the list of processes with open network connections and the corresponding domain/IP.
        """
        process_map = {}

        for conn in psutil.net_connections(kind='inet'):
            try:
                pid = conn.pid
                if pid is None:
                    continue

                proc = psutil.Process(pid)
                proc_info = proc.as_dict(attrs=['name', 'username', 'exe'])

                process_name = proc_info['name']
                process_user = proc_info['username']
                process_exe = proc_info['exe']

                remote_address = conn.raddr
                if remote_address:
                    remote_ip = remote_address.ip
                    try:
                        host = socket.gethostbyaddr(remote_ip)[0]
                    except (socket.herror, socket.gaierror):
                        host = remote_ip

                    if pid not in process_map:
                        process_map[pid] = {
                            'name': process_name,
                            'user': process_user,
                            'exe': process_exe,
                            'connections': []
                        }
                    process_map[pid]['connections'].append(host)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.data = []
        for pid, details in process_map.items():
            self.data.append({
                'Name': details['name'],
                'User': details['user'],
                'Executable Path': details['exe'],
                'Connected Hosts': details['connections'],
            })

        return self.data


class NetworkUsageWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, update_interval=5000):
        super().__init__(parent)

        self.title("Network Usage")
        self.geometry("800x600")
        self.resizable(True, True)

        self.update_interval = update_interval
        self.stop_update = False

        self.heading_label = ctk.CTkLabel(self, text="Processes Using Internet", font=("Arial", 18, "bold"))
        self.heading_label.pack(pady=10)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", rowheight=25, fieldbackground="#2e2e2e")
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333333", foreground="white")

        self.tree = ttk.Treeview(self, columns=("Name", "User", "Executable Path", "Connected Hosts"),
                                 show="headings", selectmode="browse")
        self.tree.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        self.tree.heading("Name", text="Name")
        self.tree.heading("User", text="User")
        self.tree.heading("Executable Path", text="Executable Path")
        self.tree.heading("Connected Hosts", text="Connected Hosts")

        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("User", width=100, anchor="center")
        self.tree.column("Executable Path", width=250, anchor="w")
        self.tree.column("Connected Hosts", width=200, anchor="w")

        self.detector = NetworkUsageDetector()
        self.data_queue = queue.Queue()

        # Start a background thread for periodic updates
        self.update_thread = threading.Thread(target=self.fetch_data_in_background, daemon=True)
        self.update_thread.start()

        # Start periodic GUI updates
        self.update_gui_periodically()

    def fetch_data_in_background(self):
        """
        Continuously fetch data in the background and place it in the queue.
        """
        while not self.stop_update:
            network_data = self.detector.get_connected_urls()
            self.data_queue.put(network_data)
            threading.Event().wait(self.update_interval / 1000)

    def update_gui_periodically(self):
        """
        Periodically update the GUI by consuming data from the queue.
        """
        if not self.data_queue.empty():
            network_data = self.data_queue.get()
            self.populate_table(network_data)
        if not self.stop_update:
            self.after(100, self.update_gui_periodically)

    def populate_table(self, network_data):
        """
        Populate the Treeview with the latest network data.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        for entry in network_data:
            self.tree.insert("", "end", values=(
                entry['Name'],
                entry['User'] or "None",
                entry['Executable Path'],
                ", ".join(entry['Connected Hosts']),
            ))

    def destroy(self):
        """
        Gracefully stop the update thread and close the window.
        """
        self.stop_update = True
        super().destroy()


