"""
Stub implementation for DearPyGui-based UI, to be implemented later.
Implements the BaseView interface for future UI backend swapping.
"""
from view.base_view import BaseView

# Uncomment below after installing DearPyGui
# import dearpygui.dearpygui as dpg

class DearPyGuiView(BaseView):
    def __init__(self):
        # TODO: Initialize DearPyGui context and create main window
        pass

    def geometry(self, dimensions: str) -> None:
        # TODO: Map window size and position
        pass

    def protocol(self, protocol_name: str, callback) -> None:
        # TODO: Handle close protocol or ignore if not supported
        pass

    def on_select_folder(self, callback):
        # TODO: Implement folder selection dialog in DearPyGui
        pass

    def on_next(self, callback):
        # TODO: Bind "Next" button or key to callback
        pass

    def on_prev(self, callback):
        # TODO: Bind "Previous" button or key to callback
        pass

    def add_reset_button(self, callback):
        # TODO: Add a reset button to UI and bind to callback
        pass

    def ask_for_folder(self) -> str:
        # TODO: Open folder dialog and return selected path
        return ""

    def show_image(self, photo):
        # TODO: Render image thumbnail in DearPyGui
        pass

    def update_status(self, text: str, file_size_kb=None):
        # TODO: Display status text in UI
        pass

    def set_categories(self, categories):
        # TODO: Create category buttons or list
        pass

    def bind_category(self, idx, on_click, on_right_click):
        # TODO: Bind category selection events
        pass

    def bind_keyboard_shortcuts(self):
        # TODO: Bind key shortcuts (1-9, arrows)
        pass

    def bind(self, sequence: str, func=None, add=None) -> None:
        # TODO: Map event binding if supported
        pass

    def destroy(self):
        # TODO: Clean up DearPyGui context
        pass

    def quit(self) -> None:
        # TODO: Stop DearPyGui main loop and exit
        pass

    def winfo_width(self) -> int:
        # TODO: Return current window width
        return 0

    def winfo_height(self) -> int:
        # TODO: Return current window height
        return 0

    def winfo_x(self) -> int:
        # TODO: Return window X position
        return 0

    def winfo_y(self) -> int:
        # TODO: Return window Y position
        return 0
