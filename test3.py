import customtkinter as ctk
import psutil
import socket
import time
import threading
from tkinter import ttk, Menu


class NetworkUsageDetector:
    def __init__(self):
        self.data = []

    def get_connected_urls(self):
        """
        Get the list of processes with open network connections and the corresponding domain/IP.
        """
        process_map = {}

        for conn in psutil.net_connections(kind='inet'):  # Get internet connections (TCP/UDP)
            try:
                # Get the associated process ID (pid) for the connection
                pid = conn.pid
                if pid is None:
                    continue

                proc = psutil.Process(pid)
                proc_info = proc.as_dict(attrs=['name', 'username', 'exe'])  # Use as_dict to get process info

                process_name = proc_info['name']
                process_user = proc_info['username']
                process_exe = proc_info['exe']

                # Get the remote address (IP and Port)
                remote_address = conn.raddr
                if remote_address:
                    remote_ip = remote_address.ip
                    try:
                        # Try to resolve the IP address to a domain name
                        host = socket.gethostbyaddr(remote_ip)[0]
                    except (socket.herror, socket.gaierror):
                        host = remote_ip  # If domain lookup fails, show the IP instead

                    # Group by process
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

        # Create a structured temporary database
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
        self.geometry("800x600")  # Set desired size
        self.resizable(True, True)

        # Set update interval (in milliseconds)
        self.update_interval = update_interval

        # Create heading label
        self.heading_label = ctk.CTkLabel(self, text="Processes Using Internet", font=("Arial", 18, "bold"))
        self.heading_label.pack(pady=10)

        # Style configuration for Treeview (Dark Theme)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", rowheight=25, fieldbackground="#2e2e2e")
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333333", foreground="white")

        # Create Treeview for the table
        self.tree = ttk.Treeview(self, columns=("Name", "User", "Executable Path", "Connected Hosts"), show="headings", selectmode="browse")
        self.tree.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Set column headings
        self.tree.heading("Name", text="Name")
        self.tree.heading("User", text="User")
        self.tree.heading("Executable Path", text="Executable Path")
        self.tree.heading("Connected Hosts", text="Connected Hosts")

        # Set column widths
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("User", width=100, anchor="center")
        self.tree.column("Executable Path", width=250, anchor="w")
        self.tree.column("Connected Hosts", width=200, anchor="w")

        # Loading label
        self.loading_label = ctk.CTkLabel(self, text="Refreshing...", font=("Arial", 14), fg_color="#333333")
        self.loading_label.place_forget()  # Initially hide the label

        # Start periodic updates
        self.populate_table_thread()

    def populate_table(self):
        # Display loading label
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.tree.state(["disabled"])  # Disable the table during refresh

        # Clear current data in the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch data from the detector
        detector = NetworkUsageDetector()
        network_data = detector.get_connected_urls()

        for entry in network_data:
            # Insert row data
            row_id = self.tree.insert("", "end", values=(
                entry['Name'],
                entry['User'] or "None",
                entry['Executable Path'],
                ", ".join(entry['Connected Hosts']),
            ))

        # Hide loading label and re-enable the table
        self.loading_label.place_forget()
        self.tree.state(["!disabled"])

    def update_table_periodically(self):
        # Fetch and update the table data
        self.populate_table()

        # Schedule the next update
        self.after(self.update_interval, self.update_table_periodically)

    def populate_table_thread(self):
        # Run populate_table in a separate thread to prevent the GUI from freezing
        thread = threading.Thread(target=self.populate_table)
        thread.daemon = True
        thread.start()


def open_network_usage():
    NetworkUsageWindow()


# Example usage
if __name__ == "__main__":
    app = ctk.CTk()  # Main application window
    app.geometry("400x300")
    app.title("Main Window")

    # Button to open the Network Usage Window
    open_button = ctk.CTkButton(app, text="Open Network Usage", command=open_network_usage)
    open_button.pack(pady=20)

    app.mainloop()
