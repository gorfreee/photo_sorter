# dialogs.py
# Contains dialog functions for showing info, warning, error messages, and category configuration dialogs.
# This file keeps UI dialog logic modular and reusable within the view layer.

import dearpygui.dearpygui as dpg
from typing import Dict, Callable
import tkinter as tk
from tkinter import filedialog


def _show_message_dialog(title: str, message: str, width: int = 300, height: int = 100) -> None:
    """Helper function to show a modal dialog with a message and OK button."""
    window_id = dpg.generate_uuid()

    def _close_dialog():
        if dpg.does_item_exist(window_id):
            dpg.delete_item(window_id)

    with dpg.window(label=title, modal=True, show=True, width=width, height=height, tag=window_id):
        dpg.add_text(message)
        dpg.add_button(label="OK", callback=_close_dialog)


def show_info(message: str) -> None:
    """Show an information dialog with the given message."""
    _show_message_dialog("Info", message)


def show_warning(message: str) -> None:
    """Show a warning dialog with the given message."""
    _show_message_dialog("Warning", message)


def show_error(message: str) -> None:
    """Show an error dialog with the given message."""
    _show_message_dialog("Error", message)


def configure_category(idx: int, initial: Dict[str, str], callback: Callable) -> None:
    """
    Show a dialog to configure category name and path.
    Calls the callback with a dict: {'action': 'save'|'delete'|'cancel', ...data}
    """
    name_value = initial.get('name', '')
    path_value = initial.get('path', '')
    window_id = dpg.generate_uuid()

    def save_callback():
        result = {
            'action': 'save',
            'name': dpg.get_value(f"cat_name_{window_id}"),
            'path': dpg.get_value(f"cat_path_{window_id}")
        }
        dpg.delete_item(window_id)
        callback(result)

    def delete_callback():
        result = {'action': 'delete'}
        dpg.delete_item(window_id)
        callback(result)

    def cancel_callback():
        dpg.delete_item(window_id)
        callback({'action': 'cancel'})

    def browse_callback():
        # Use native Windows folder selection dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        folder_selected = filedialog.askdirectory(title="Select Destination Folder")
        root.destroy()
        if folder_selected:
            dpg.set_value(f"cat_path_{window_id}", folder_selected)

    with dpg.window(label=f"Edit Category {idx+1}", modal=True, tag=window_id, width=400, height=200):
        dpg.add_input_text(label="Category Name", default_value=name_value, tag=f"cat_name_{window_id}")
        dpg.add_input_text(label="Destination Folder", default_value=path_value, tag=f"cat_path_{window_id}")
        dpg.add_button(label="Browse", callback=browse_callback)
        dpg.add_button(label="Save", callback=save_callback)
        dpg.add_button(label="Delete", callback=delete_callback)
        dpg.add_button(label="Cancel", callback=cancel_callback)
