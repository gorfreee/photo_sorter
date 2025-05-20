# config.py
# Handles loading and saving the application's configuration (categories, last folder, etc.).
# This file centralizes config management to keep the rest of the code clean and maintainable.

import json
from pathlib import Path

# Path to the configuration file stored in the user's home directory
CONFIG_PATH = Path.home() / ".photosorter_config.json"

def load_config() -> dict:
    """
    Load configuration from the JSON file. If it doesn't exist, return default structure.
    """
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"categories": [], "last_folder": ""}


def save_config(cfg: dict) -> None:
    """
    Save configuration to the JSON file, creating it if necessary.
    """
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)
