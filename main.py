import os
import importlib
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

# Path to the features folder
FEATURES_PATH = "features"


# Load features dynamically
def load_features():
    features = {}
    for file in os.listdir(FEATURES_PATH):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = f"{FEATURES_PATH}.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # Check required attributes
                if all(hasattr(module, attr) for attr in ["name", "on_text", "off_text", "is_on", "onEnable", "onDisable"]):
                    features[module.name] = module
                else:
                    print(f"Skipping {file}: Missing required attributes")
            except Exception as e:
                print(f"Failed to load {file}: {e}")
    return features

# Toggle feature state
def toggle_feature(feature, button):
    if feature.is_on:
        feature.onDisable()
        feature.is_on = False
        button.configure(text=feature.off_text, fg_color="red")
    else:
        feature.onEnable()
        feature.is_on = True
        button.configure(text=feature.on_text, fg_color="green")

# Create the modern GUI
def create_gui(features):
    # Configure customtkinter appearance
    ctk.set_appearance_mode("System")  # Modes: "System", "Light", "Dark"
    ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

    # Create the main window
    root = ctk.CTk()
    root.title("Feature Manager")
    root.geometry("600x400")
    root.resizable(False, False)

    try:
        root.iconbitmap("logo.ico")
        # Load the image using Pillow (ensure it is a compatible format)
        ico = Image.open('logo.png')  # Use your path to the logo image (can be .jpeg, .png, etc.)

        # Resize or process the image (optional, to ensure it's the right size)
        ico = ico.resize((32, 32))  # You can resize to a suitable icon size if needed
        
        # Convert to PhotoImage object
        photo = ImageTk.PhotoImage(ico)

        # Set the icon using wm_iconphoto
        root.iconphoto(False, photo)

    except Exception as e:
        print(f"Error setting icon: {e}")


    # Add a title label
    title_label = ctk.CTkLabel(root, text="Feature Manager", font=ctk.CTkFont(size=24, weight="bold"))
    title_label.pack(pady=20)

    # Create a scrollable frame for features
    feature_frame = ctk.CTkScrollableFrame(root, width=500, height=300, label_text="Features")
    feature_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Populate features dynamically
    for feature_name, feature in features.items():
        frame = ctk.CTkFrame(feature_frame)
        frame.pack(pady=5, padx=10, fill="x")
        
        label = ctk.CTkLabel(frame, text=feature_name, anchor="w", font=ctk.CTkFont(size=14))
        label.pack(side="left", padx=10)

        button = ctk.CTkButton(
            frame,
            text=feature.on_text if feature.is_on else feature.off_text,
            fg_color="green" if feature.is_on else "red",
            width=100,
            command=lambda f=feature, b=None: toggle_feature(f, b)
        )
        button.pack(side="right", padx=10)
        # Pass the button instance to toggle function
        button.configure(command=lambda f=feature, b=button: toggle_feature(f, b))

    root.mainloop()

if __name__ == "__main__":
    features = load_features()
    if not features:
        messagebox.showerror("Error", "No valid features found!")
    else:
        create_gui(features)
