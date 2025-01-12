import os
import importlib
import tkinter as tk
from tkinter import messagebox

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
        button.config(text=feature.off_text, bg="red")
    else:
        feature.onEnable()
        feature.is_on = True
        button.config(text=feature.on_text, bg="green")

# Create the GUI
def create_gui(features):
    root = tk.Tk()
    root.title("Feature Manager")
    for feature_name, feature in features.items():
        frame = tk.Frame(root, pady=5)
        frame.pack()
        label = tk.Label(frame, text=feature_name, width=20, anchor="w")
        label.pack(side="left")
        button = tk.Button(
            frame,
            text=feature.on_text if feature.is_on else feature.off_text,
            bg="green" if feature.is_on else "red",
            command=lambda f=feature, b=None: toggle_feature(f, b),
        )
        button.pack(side="right")
        # Pass the button instance to toggle function
        button.config(command=lambda f=feature, b=button: toggle_feature(f, b))
    root.mainloop()

if __name__ == "__main__":
    features = load_features()
    if not features:
        messagebox.showerror("Error", "No valid features found!")
    else:
        create_gui(features)
