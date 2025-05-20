# utils.py
# Provides utility functions used throughout the app, such as filename sanitization.
# This file keeps small, reusable helpers separate from main logic for clarity and reusability.

from pathlib import Path
import re


def sanitize_filename(name: str) -> str:
    """
    Remove or replace invalid characters for filenames.
    """
    return re.sub(r'[\\/:*?"<>|]', '_', name)
