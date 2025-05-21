"""
main_window.py
DearPyGui-based UI for Photo Sorter application.
"""
from typing import Dict, Optional, Callable, Any, Union
import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image

class MainWindow:
    def __init__(self):
        self._init_callbacks()
        self._texture_registry: Dict[str, str] = {}
        self._current_image: Optional[str] = None
        self._image_container_tag = "image_container"
        self._texture_tag = "current_texture"
        
        # Initialize DearPyGui
        dpg.create_context()
            
        dpg.create_viewport(title="Photo Sorter", width=1200, height=800)
        dpg.setup_dearpygui()
        
        # Create texture registry
        with dpg.texture_registry(show=False):
            # Create an initial blank texture
            blank_data = [0.0] * (100 * 100 * 3)
            dpg.add_static_texture(
                width=100,
                height=100,
                default_value=blank_data,
                tag=self._texture_tag
            )
        
        with dpg.window(label="Photo Sorter", tag="Primary Window"):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open Folder", callback=self._on_open_folder)
            
            # Image display area
            with dpg.group(horizontal=True):
                dpg.add_button(label="Previous", callback=self._on_previous)
                with dpg.child_window(width=800, height=600):
                    dpg.add_image(texture_tag=self._texture_tag, tag=self._image_container_tag)
                dpg.add_button(label="Next", callback=self._on_next)
        
        dpg.set_primary_window("Primary Window", True)
        dpg.show_viewport()
        
    def _load_image(self, image_path: str) -> None:
        """Load an image and update the texture"""
        try:
            # Open and convert image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get image data
            width, height = img.size
            img_data = np.array(img)
            
            # Convert to normalized float values
            float_data = [float(x)/255.0 for x in img_data.flatten()]
            
            # Update or create texture
            if dpg.does_item_exist(self._texture_tag):
                dpg.delete_item(self._texture_tag)
                
            # Create new texture
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=float_data,
                parent="texture_registry",
                tag=self._texture_tag
            )
            
            # Update image widget
            dpg.configure_item(self._image_container_tag, texture_tag=self._texture_tag)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            
    def _on_previous(self):
        """Handle previous button click"""
        if self._callbacks["on_previous"]:
            self._callbacks["on_previous"]()
            
    def _on_next(self):
        """Handle next button click"""
        if self._callbacks["on_next"]:
            self._callbacks["on_next"]()
            
    def _on_open_folder(self):
        """Handle open folder button click"""
        if self._callbacks["on_open_folder"]:
            self._callbacks["on_open_folder"]()
            
    def _init_callbacks(self):
        """Initialize callback dictionary"""
        self._callbacks: Dict[str, Optional[Callable[[], Any]]] = {
            "on_previous": None,
            "on_next": None,
            "on_open_folder": None
        }
        
    def run(self):
        """Start the DearPyGui event loop"""
        dpg.start_dearpygui()
        
    def cleanup(self):
        """Clean up DearPyGui resources"""
        dpg.destroy_context()
        
    def display_image(self, image_path: Optional[str]):
        """Display an image in the window"""
        if image_path is None:
            # Reset to blank texture
            blank_data = [0.0] * (100 * 100 * 3)
            if dpg.does_item_exist(self._texture_tag):
                dpg.delete_item(self._texture_tag)
            dpg.add_static_texture(
                width=100,
                height=100,
                default_value=blank_data,
                parent="texture_registry",
                tag=self._texture_tag
            )
            dpg.configure_item(self._image_container_tag, texture_tag=self._texture_tag)
            return
        
        self._load_image(image_path)
                
    def set_callbacks(self,
                     on_previous: Optional[Callable[[], Any]] = None,
                     on_next: Optional[Callable[[], Any]] = None,
                     on_open_folder: Optional[Callable[[], Any]] = None):
        """Set the callback functions"""
        if on_previous:
            self._callbacks["on_previous"] = on_previous
        if on_next:
            self._callbacks["on_next"] = on_next
        if on_open_folder:
            self._callbacks["on_open_folder"] = on_open_folder
            
    def open_folder_dialog(self, callback: Callable[[Any, Any], Any]):
        """Open a folder selection dialog"""
        with dpg.file_dialog(
            directory_selector=True, 
            show=True,
            callback=callback,
            tag="file_dialog"):
            dpg.add_file_extension("")
