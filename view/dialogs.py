"""
dialogs.py
Dialog windows for the Photo Sorter application.
"""
import dearpygui.dearpygui as dpg
from typing import Optional, Callable

def configure_category(callback: Optional[Callable[[str], None]] = None):
    """Show a dialog to configure a category."""
    with dpg.window(label="Configure Category", modal=True, tag="category_dialog"):
        dpg.add_text("Enter category name:")
        dpg.add_input_text(tag="category_input")
        
        def on_ok():
            if callback:
                category = dpg.get_value("category_input")
                callback(category)
            dpg.delete_item("category_dialog")
            
        def on_cancel():
            dpg.delete_item("category_dialog")
            
        with dpg.group(horizontal=True):
            dpg.add_button(label="OK", callback=on_ok)
            dpg.add_button(label="Cancel", callback=on_cancel)

def show_info(message: str):
    """Show an information dialog."""
    with dpg.window(label="Information", modal=True, tag="info_dialog"):
        dpg.add_text(message)
        
        def on_ok():
            dpg.delete_item("info_dialog")
            
        dpg.add_button(label="OK", callback=on_ok)

def show_error(message: str):
    """Show an error dialog."""
    with dpg.window(label="Error", modal=True, tag="error_dialog"):
        dpg.add_text(message, color=(255, 0, 0))
        
        def on_ok():
            dpg.delete_item("error_dialog")
            
        dpg.add_button(label="OK", callback=on_ok)
