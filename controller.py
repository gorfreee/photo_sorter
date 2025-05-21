# controller.py
# Implements the PhotoSorterController class, which coordinates the app's logic and communication between model and view.
# This file is the core of the MVC pattern, keeping logic separate from UI and data handling.

from pathlib import Path
from config import load_config, save_config
from model import list_images, move_image, create_thumbnail
from view.main_window import MainWindow
from view.dialogs import configure_category, show_info, show_error
import dearpygui.dearpygui as dpg

class PhotoSorterController:
    def __init__(self):
        # Load configuration and initialize state
        self.config = load_config()
        last_folder = self.config.get("last_folder", "")
        self.current_folder = Path(last_folder) if last_folder else None
        self.images = list_images(self.current_folder) if self.current_folder and self.current_folder.exists() else []
        self.current_index = 0

        # Initialize view (DearPyGui)
        self.view = MainWindow()
        
        # Setup callbacks
        self.view.set_callbacks(
            on_previous=self.prev_image,
            on_next=self.next_image,
            on_open_folder=self.select_folder
        )

    def select_folder(self):
        """Initiate folder selection dialog"""
        self.view.open_folder_dialog(self._on_folder_selected)

    def _on_folder_selected(self, sender, app_data):
        """Handle folder selection"""
        folder = Path(app_data['file_path_name'])
        if folder.exists():
            self.current_folder = folder
            self.images = list_images(folder)
            self.current_index = 0
            self.config["last_folder"] = str(folder)
            save_config(self.config)
            self.show_current()
        else:
            show_error("Selected folder does not exist!")

    def show_current(self):
        """Display current image"""
        if not self.images:
            self.view.display_image(None)
            return
        
        if 0 <= self.current_index < len(self.images):
            self.view.display_image(str(self.images[self.current_index]))

    def next_image(self):
        """Show next image"""
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_current()

    def prev_image(self):
        """Show previous image"""
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.show_current()

    def run(self):
        """Start the application"""
        self.show_current()
        self.view.run()

    def cleanup(self):
        """Clean up resources"""
        self.view.cleanup()
        save_config(self.config)
