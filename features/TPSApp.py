
import customtkinter as ctk
from tkinter import ttk, Menu
from TaskNoticer.TaskManager import ThirdPartySoftwareDetector
import time


name = "Third Party Apps Data"
on_text = "Exit"
off_text = "View"
is_on = False
import os

    


def onDisable():
    os.system("nircmd.exe mutesysvolume 1")




class LocalDatabaseWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, update_interval=5000):
        super().__init__(parent)

        # Configure the window
        self.title("Local Database")
        self.geometry("800x600")  # Set desired size
        self.resizable(True, True)

        # Set update interval (in milliseconds)
        self.update_interval = update_interval

        # Create heading label
        self.heading_label = ctk.CTkLabel(self, text="Third Party Softwares", font=("Arial", 18, "bold"))
        self.heading_label.pack(pady=10)

        # Style configuration for Treeview (Dark Theme)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", rowheight=25, fieldbackground="#2e2e2e")
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333333", foreground="white")

        # Create Treeview for the table
        self.tree = ttk.Treeview(
            self, columns=("Name", "User", "Path", "PIDs"), show="headings", selectmode="browse"
        )
        self.tree.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Set column headings
        self.tree.heading("Name", text="Name")
        self.tree.heading("User", text="User")
        self.tree.heading("Path", text="Path")
        self.tree.heading("PIDs", text="PIDs")

        # Set column widths
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("User", width=100, anchor="center")
        self.tree.column("Path", width=250, anchor="w")
        self.tree.column("PIDs", width=100, anchor="center")

        # Style for tags
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("yellow", foreground="gold")

        # Right-click menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)

        # Bind right-click to show context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Loading label
        self.loading_label = ctk.CTkLabel(self, text="Refreshing...", font=("Arial", 14), fg_color="#333333")
        self.loading_label.place_forget()  # Initially hide the label

        # Start periodic updates
        self.populate_table()
        self.update_table_periodically()

    def populate_table(self):
        # Display loading label
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.tree.state(["disabled"])  # Disable the table during refresh

        # Simulate a small delay for refresh effect
        self.update_idletasks()
        time.sleep(0.2)  # Pause for 200ms (adjustable)

        # Clear current data in the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch data from the detector
        detector = ThirdPartySoftwareDetector()
        database = detector.fetch_data()

        for app in database:
            # Insert row data
            row_id = self.tree.insert(
                "",
                "end",
                values=(
                    app["Name"],
                    app["User"] or "None",
                    app["Path"],
                    ", ".join(map(str, app["PIDs"])),
                ),
            )

            # Apply color coding
            if app["None_User"]:
                self.tree.item(row_id, tags=("red",))  # Apply red to the row
            if app["Multiple_PIDs"]:
                self.tree.item(row_id, tags=("yellow",))  # Apply yellow to the row

        # Hide loading label and re-enable the table
        self.loading_label.place_forget()
        self.tree.state(["!disabled"])

    def update_table_periodically(self):
        # Fetch and update the table data
        self.populate_table()
        # Schedule the next update
        self.after(self.update_interval, self.update_table_periodically)

    def show_context_menu(self, event):
        # Get selected row
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_path(self):
        selected_item = self.tree.selection()
        if selected_item:
            path = self.tree.item(selected_item[0], "values")[2]  # "Path" is in column index 2
            self.clipboard_clear()
            self.clipboard_append(path)
            self.update()  # Required to update the clipboard content


def open_local_database():
    LocalDatabaseWindow()
# Example usage
if __name__ == "__main__":
    app = ctk.CTk()  # Main application window
    app.geometry("400x300")
    app.title("Main Window")

    def open_local_database():
        LocalDatabaseWindow(app)

    # Button to open the Local Database Window
    open_button = ctk.CTkButton(app, text="Open Local Database", command=open_local_database)
    open_button.pack(pady=20)

    app.mainloop()



def onEnable():
    open_local_database()