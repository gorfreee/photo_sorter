"""
config.py

This module manages the application's configuration, such as user-defined categories, the last accessed folder, and window size.
It centralizes all configuration-related logic to keep the rest of the codebase clean and maintainable.
Configuration is stored as a JSON file in the user's home directory, allowing persistent settings across sessions.
Use this module to load and save configuration data in a consistent and reliable way.
"""

# --- Imports ---
# Import standard libraries for JSON handling and file path management.
import json
from pathlib import Path

# --- Configuration File Path ---
# Define the path to the configuration file in the user's home directory.
CONFIG_PATH = Path.home() / ".photosorter_config.json"

# --- Configuration Load Function ---
# Loads configuration from the JSON file if it exists, otherwise returns default settings.
# Ensures 'ui_backend' is set to 'tkinter' by default for future UI backend selection.
def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
        cfg.setdefault("ui_backend", "tkinter")
        return cfg
    return {"categories": [], "last_folder": "", "window_size": [800, 600], "ui_backend": "tkinter"}

# --- Configuration Save Function ---
# Saves the provided configuration dictionary to the JSON file, creating it if necessary.
def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)
