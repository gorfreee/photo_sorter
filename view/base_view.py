"""
Defines the abstract interface for all view implementations.
This allows swapping out the UI backend (e.g., Dear PyGui or others)
without changing controller logic.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, Callable

class BaseView(ABC):
    @abstractmethod
    def protocol(self, protocol_name: str, callback: Optional[Callable] = None) -> None:
        """Register protocol handler."""
        pass

    @abstractmethod
    def on_select_folder(self, callback: Callable) -> None:
        pass

    @abstractmethod
    def on_next(self, callback: Callable) -> None:
        pass

    @abstractmethod
    def on_prev(self, callback: Callable) -> None:
        pass

    @abstractmethod
    def add_reset_button(self, callback: Callable) -> None:
        pass

    @abstractmethod
    def ask_for_folder(self) -> str:
        pass

    @abstractmethod
    def show_image(self, photo) -> None:
        pass

    @abstractmethod
    def update_status(self, text: str, file_size_kb: Optional[float] = None) -> None:
        pass

    @abstractmethod
    def set_categories(self, categories: list) -> None:
        pass

    @abstractmethod
    def bind_category(self, idx: int, on_click: Callable[[int], None], on_right_click: Callable[[int], None]) -> None:
        pass

    @abstractmethod
    def bind_keyboard_shortcuts(self) -> None:
        pass

    @abstractmethod
    def destroy(self) -> None:
        pass

    @abstractmethod
    def quit(self) -> None:
        """Quit the application or main loop."""
        pass

    @abstractmethod
    def mainloop(self, n: int = 0, **kwargs) -> None:
        """Start the main event loop for the UI."""
        pass

    @abstractmethod
    def set_selected_folder_path(self, folder_path: str) -> None:
        """Update the displayed selected folder path next to the Select Folder button."""
        pass
