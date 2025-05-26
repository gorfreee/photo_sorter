"""
Utility Functions for Photo Sorter

This file contains small, reusable helper functions that support the main application logic.
By keeping utility functions here, the codebase remains organized, and common operations (such as filename sanitization) can be reused easily throughout the app.
"""

# Import standard libraries needed for utility operations.
from pathlib import Path
import re


# Define a function to sanitize filenames by removing or replacing invalid characters.
def sanitize_filename(name: str) -> str:
    """
    Remove or replace invalid characters for filenames.
    """
    return re.sub(r'[\\/:*?"<>|]', '_', name)
