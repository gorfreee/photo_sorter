"""
Factory module to create view implementations based on configuration.
Allows swapping UI backends (e.g., Tkinter, Dear PyGui) without changing controller logic.
"""
from config import load_config
from view.base_view import BaseView

# Import available view implementations
from view.main_window import MainWindow
try:
    from view.dearpygui_view import DearPyGuiView
except ImportError:
    DearPyGuiView = None


def create_view(config: dict) -> BaseView:
    """
    Create and return a view instance based on the 'ui_backend' setting in config.
    Defaults to Tkinter-based MainWindow if the requested backend is unavailable.
    """
    backend = config.get("ui_backend", "tkinter")
    if backend == "dearpygui" and DearPyGuiView:
        return DearPyGuiView()
    return MainWindow()
