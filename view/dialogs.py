# dialogs.py
# Contains dialog functions for showing info, warning, error messages, and category configuration dialogs.
# This file keeps UI dialog logic modular and reusable within the view layer.

from typing import Dict, Callable
from tkinter import filedialog
import dearpygui.dearpygui as dpg
import uuid


def _center_window(window_id: str, width: int, height: int) -> None:
    """Utility to center a DearPyGui window in the viewport."""
    vp_width = dpg.get_viewport_client_width()
    vp_height = dpg.get_viewport_client_height()
    x = max((vp_width - width) // 2, 0)
    y = max((vp_height - height) // 2, 0)
    dpg.set_item_pos(window_id, [x, y])


def _show_message_dialog(title: str, message: str, width: int = 300, height: int = 100) -> None:
    """Helper function to show a modal dialog with a message and OK button, centered."""
    window_id = str(dpg.generate_uuid())

    def _close_dialog():
        dpg.delete_item(window_id)

    with dpg.window(label=title, modal=True, show=True, width=width, height=height, tag=window_id):
        dpg.add_text(message)
        dpg.add_spacer(height=10)
        dpg.add_button(label="OK", callback=_close_dialog)
    # Center after creation
    _center_window(window_id, width, height)


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
    Show a modal dialog to configure a category, centered.
    Includes: name input, destination folder input with Browse button (native Windows folder dialog),
    and OK, Cancel, Delete buttons.
    """
    import dearpygui.dearpygui as dpg
    import uuid
    import tkinter as tk
    from tkinter import filedialog

    # Unique window/tag IDs to avoid alias conflicts
    window_id = f"category_config_{idx}_{uuid.uuid4()}"
    name_id = f"cat_name_{window_id}"
    folder_id = f"cat_folder_{window_id}"
    ok_id = f"cat_ok_{window_id}"

    width, height = 315, 175

    def _on_ok():
        callback({
            "action": "save",
            "idx": idx,
            "name": dpg.get_value(name_id),
            "path": dpg.get_value(folder_id)  # Changed from 'folder' to 'path'
        })
        dpg.delete_item(window_id)

    def _on_cancel():
        callback({"action": "cancel", "idx": idx})
        dpg.delete_item(window_id)

    def _on_delete():
        callback({"action": "delete", "idx": idx})
        dpg.delete_item(window_id)

    def _on_browse():
        # Use native Windows folder selection dialog via tkinter
        root = tk.Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory(title="Select Destination Folder")
        root.destroy()
        if folder_selected:
            dpg.set_value(folder_id, folder_selected)
            _update_ok_state()  # Update OK state after browsing

    def _update_ok_state():
        # Enable OK only if both fields are non-empty
        name_val = dpg.get_value(name_id)
        folder_val = dpg.get_value(folder_id)
        enabled = bool(name_val.strip()) and bool(folder_val.strip())
        dpg.configure_item(ok_id, enabled=enabled)

    with dpg.window(label=f"Edit Category {idx+1}", modal=True, tag=window_id, width=width, height=height, no_resize=True, no_collapse=True):
        dpg.add_text("Category Name:")
        dpg.add_input_text(tag=name_id, default_value=initial.get("name", ""), width=300, callback=lambda s,a,u: _update_ok_state())
        dpg.add_spacer(height=5)
        dpg.add_text("Destination Folder:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag=folder_id, default_value=initial.get("path", ""), width=220, callback=lambda s,a,u: _update_ok_state())  # Use 'path' for initial value
            dpg.add_button(label="Browse...", callback=_on_browse)
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="OK", tag=ok_id, callback=_on_ok)
            dpg.add_button(label="Cancel", callback=_on_cancel)
            dpg.add_button(label="Delete", callback=_on_delete)
    # Center after creation
    _center_window(window_id, width, height)
    # Set initial OK state
    _update_ok_state()
