# controller.py
# Implements the PhotoSorterController class, which coordinates the app's logic and communication between model and view.
# This file is the core of the MVC pattern, keeping logic separate from UI and data handling.

from pathlib import Path
from config import load_config, save_config
from model import list_images, move_image, create_thumbnail
from view.factory import create_view
from view.dialogs import configure_category, show_error
from typing import Callable
import threading  # For background thumbnail preloading

class PhotoSorterController:
    THUMBNAIL_PRELOAD_COUNT = 15  # Number of thumbnails to preload for instant navigation

    def __init__(self):
        # Load configuration and initialize state
        self.config = load_config()
        last_folder = self.config.get("last_folder", "")
        self.current_folder = None
        self.images = []
        self.current_index = 0
        self.thumbnail_cache = {}  # Cache for thumbnails
        # Instantiate view using factory for pluggable UI backends
        self.view = create_view(self.config)
        # TODO: In the future, replace MainWindow with BaseView implementation (e.g., DearPyGuiView)
        # self.view = create_view()  # Factory to choose view by configuration
        # Apply saved window size and position
        width, height = self.config.get("window_size", [800, 600])
        x, y = self.config.get("window_position", [None, None])
        if x is not None and y is not None:
            self.view.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.view.geometry(f"{width}x{height}")
        # Save window size and position on close
        self.view.protocol("WM_DELETE_WINDOW", self.on_close)
        self.view.on_select_folder(self.select_folder)
        self.view.on_next(self.next_image)
        self.view.on_prev(self.prev_image)
        
        # Build category buttons
        self.build_category_buttons()

        # Hook reset button to reset_categories_and_source
        self.view.add_reset_button(self.reset_categories_and_source)

        # Show first image if available
        if self.images:
            self.show_current()

    def select_folder(self):
        folder = self.view.ask_for_folder()
        if folder:
            self.current_folder = Path(folder)
            self.config["last_folder"] = str(folder)
            save_config(self.config)
            self.images = list_images(self.current_folder)
            self.current_index = 0
            self.thumbnail_cache = {}  # Clear cache when new folder is selected
            # Show the first image immediately for instant feedback
            self.show_current()
            # Preload thumbnails for the remaining images in the background (excluding the first)
            def preload_thumbnails():
                for img_path in self.images[1:self.THUMBNAIL_PRELOAD_COUNT]:
                    if img_path not in self.thumbnail_cache:
                        try:
                            self.thumbnail_cache[img_path] = create_thumbnail(img_path)
                        except Exception:
                            self.thumbnail_cache[img_path] = None
            if len(self.images) > 1:
                threading.Thread(target=preload_thumbnails, daemon=True).start()

    def show_current(self):
        if not self.images:
            self.view.show_image(None)
            self.view.update_status("No images found.")
            return
        img_path = self.images[self.current_index]
        # Use cached thumbnail if available, else load and cache it
        pil_thumb = self.thumbnail_cache.get(img_path)
        if pil_thumb is None:
            try:
                pil_thumb = create_thumbnail(img_path)
            except Exception:
                pil_thumb = None
            self.thumbnail_cache[img_path] = pil_thumb
        self.view.show_image(pil_thumb)
        # Get file size in kilobytes
        try:
            file_size_kb = img_path.stat().st_size / 1024
        except Exception:
            file_size_kb = None
        self.view.update_status(f"{img_path.name} ({self.current_index+1}/{len(self.images)})", file_size_kb=file_size_kb)

    def next_image(self):
        if not self.images:
            return
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            # Optionally, preload next thumbnail if approaching end of cache
            if (self.current_index + 1 < len(self.images)
                and self.images[self.current_index + 1] not in self.thumbnail_cache
                and self.current_index + 1 < self.THUMBNAIL_PRELOAD_COUNT + 10):
                try:
                    self.thumbnail_cache[self.images[self.current_index + 1]] = create_thumbnail(self.images[self.current_index + 1])
                except Exception:
                    self.thumbnail_cache[self.images[self.current_index + 1]] = None
            self.show_current()

    def prev_image(self):
        if not self.images:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current()

    def build_category_buttons(self, event=None):
        categories = self.config.get("categories", [])
        self.view.set_categories(categories)
        for idx in range(9):
            self.view.bind_category(idx, self.on_category_click, self.on_category_right)
        # Activate keyboard shortcuts
        self.view.bind_keyboard_shortcuts()

    def on_category_click(self, idx):
        categories = self.config.get("categories", [])
        if idx < len(categories) and categories[idx].get("name") and categories[idx].get("path"):
            self.assign_category(idx)
        else:
            self.edit_category(idx)

    def on_category_right(self, idx):
        self.edit_category(idx)

    def edit_category(self, idx):
        current_name = self.config["categories"][idx]["name"] if idx < len(self.config["categories"]) else ""
        current_path = self.config["categories"][idx]["path"] if idx < len(self.config["categories"]) else ""
        
        # The callback for configure_category expects a dictionary.
        def _handle_category_config_result(result: dict):
            action = result.get('action')
            if action == 'save':
                new_name = result.get('name', '')
                new_path = result.get('path', '')
                if idx >= len(self.config["categories"]):
                    self.config["categories"].extend([{"name": "", "path": ""}] * (idx + 1 - len(self.config["categories"])))
                self.config["categories"][idx] = {"name": new_name, "path": str(Path(new_path))} # Ensure path is string
                save_config(self.config)
                self.build_category_buttons() # Rebuild to reflect changes
            elif action == 'delete':
                if idx < len(self.config["categories"]):
                    self.config["categories"][idx] = {"name": "", "path": ""} # Clear the category
                    save_config(self.config)
                    self.build_category_buttons()
            # 'cancel' action does nothing here

        configure_category(idx, {"name": current_name, "path": current_path}, _handle_category_config_result)

    def assign_category(self, idx):
        if not self.images or not (0 <= idx < len(self.config["categories"])):
            return
        
        category = self.config["categories"][idx]
        if not category["name"] or not category["path"]:
            show_error("Category Not Configured: Please configure this category (name and path) before assigning images.")
            return

        img_path = self.images[self.current_index]
        dest_folder = Path(category["path"])
        
        try:
            move_image(img_path, dest_folder)
            # Remove moved image from list and update display
            self.images.pop(self.current_index)
            if not self.images: # No more images
                self.view.show_image(None)
                self.view.update_status("All images sorted from this folder!")
                self.current_folder = None # Reset current folder
                self.config["last_folder"] = "" # Clear last folder from config
                save_config(self.config)
                return

            if self.current_index >= len(self.images):
                self.current_index = len(self.images) - 1
            
            self.show_current() # Show next or previous image
        except Exception as e:
            show_error(f"Error Moving Image: Could not move {img_path.name}: {e}")
    
    def reset_categories_and_source(self):
        self.config["categories"] = []
        self.config["last_folder"] = ""
        save_config(self.config)
        
        self.current_folder = None
        self.images = []
        self.current_index = 0
        
        self.build_category_buttons()
        self.view.show_image(None)
        self.view.update_status("Select a source folder")

    def on_close(self):
        """Handle window close event by saving window size and position, then closing the application."""
        # Get current window size and position
        width = self.view.winfo_width()
        height = self.view.winfo_height()
        x = self.view.winfo_x()
        y = self.view.winfo_y()
        # Save to config
        self.config["window_size"] = [width, height]
        self.config["window_position"] = [x, y]
        save_config(self.config)
        # self.view.destroy() # This line was causing recursion, removed.
        # The view's actual destruction will be handled by the UI library's shutdown process.
