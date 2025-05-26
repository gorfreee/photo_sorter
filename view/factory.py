"""
Factory module to create view implementations based on configuration.
Allows swapping UI backends with different implementations without changing controller logic.
"""
from config import load_config
from view.base_view import BaseView
from view.dearpygui_view import DearPyGuiView

def create_view(config: dict) -> BaseView:
    """
    Create and return a view instance based on configuration.
    Currently uses Dear PyGui by default.
    """
    return DearPyGuiView()
