"""
Defines the abstract interface for all view implementations.
This allows swapping out the Tkinter-based UI for Dear PyGui or others
without changing controller logic.
"""
from abc import ABC, abstractmethod

class BaseView(ABC):
    @abstractmethod
    def geometry(self, new_geometry=None) -> str:
        """Set or get window geometry. Returns geometry string."""
        pass

    @abstractmethod
    def protocol(self, protocol_name, callback=None) -> None:
        """Register protocol handler."""
        pass

    @abstractmethod
    def on_select_folder(self, callback):
        pass

    @abstractmethod
    def on_next(self, callback):
        pass

    @abstractmethod
    def on_prev(self, callback):
        pass

    @abstractmethod
    def add_reset_button(self, callback):
        pass

    @abstractmethod
    def ask_for_folder(self) -> str:
        pass

    @abstractmethod
    def show_image(self, photo):
        pass

    @abstractmethod
    def update_status(self, text: str, file_size_kb=None):
        pass

    @abstractmethod
    def set_categories(self, categories):
        pass

    @abstractmethod
    def bind_category(self, idx, on_click, on_right_click):
        pass

    @abstractmethod
    def bind_keyboard_shortcuts(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def quit(self) -> None:
        """Quit the application or main loop."""
        pass

    @abstractmethod
    def winfo_width(self) -> int:
        pass

    @abstractmethod
    def winfo_height(self) -> int:
        pass

    @abstractmethod
    def winfo_x(self) -> int:
        pass

    @abstractmethod
    def winfo_y(self) -> int:
        pass

    @abstractmethod
    def mainloop(self, n=0, **kwargs):
        """Start the main event loop for the UI."""
        pass
