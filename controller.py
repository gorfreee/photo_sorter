# controller.py
# Implements the PhotoSorterController class, which coordinates the app's logic and communication between model and view.
# This file is the core of the MVC pattern, keeping logic separate from UI and data handling.

from pathlib import Path
from config import load_config, save_config
from model import list_images, move_image, create_thumbnail
from view.factory import create_view
from view.dialogs import configure_category, show_info, show_error
from typing import Callable

class PhotoSorterController:
    def __init__(self):
        # Load configuration and initialize state
        self.config = load_config()
        last_folder = self.config.get("last_folder", "")
        self.current_folder = Path(last_folder) if last_folder else None
        self.images = list_images(self.current_folder) if self.current_folder and self.current_folder.exists() else []
        self.current_index = 0

        # Initialize view, set window size and position from config, and bind close event
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
            self.show_current()

    def show_current(self):
        if not self.images:
            self.view.show_image(None)
            self.view.update_status("No images found.")
            return
        img_path = self.images[self.current_index]
        pil_thumb = create_thumbnail(img_path)
        # Pass PIL Image directly to the view (DearPyGui handles PIL images)
        self.view.show_image(pil_thumb)
        # Get file size in kilobytes
        try:
            file_size_kb = img_path.stat().st_size / 1024
        except Exception:
            file_size_kb = None
        self.view.update_status(f"{img_path.name} ({self.current_index+1}/{len(self.images)})", file_size_kb=file_size_kb)

    def next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            # Update display after moving index
            self.show_current()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            # Update display after moving index
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
        categories = self.config.get("categories", [])
        initial = categories[idx] if idx < len(categories) else {"name": "", "path": ""}
        # Use callback-based dialog for DearPyGui
        def on_dialog_result(result):
            if result.get("action") == "save":
                while len(categories) <= idx:
                    categories.append({"name": "", "path": ""})
                categories[idx] = {"name": result["name"], "path": result["path"]}
                self.config["categories"] = categories
                save_config(self.config)
                self.build_category_buttons()
            elif result.get("action") == "delete":
                if idx < len(categories):
                    categories[idx] = {"name": "", "path": ""}
                    self.config["categories"] = categories
                    save_config(self.config)
                    self.build_category_buttons()
            # No action needed for cancel
        configure_category(self.view, idx, initial, on_dialog_result)

    def assign_category(self, idx):
        if not self.images:
            return
        categories = self.config.get("categories", [])
        cat = categories[idx]
        dest = Path(cat["path"])
        src = self.images[self.current_index]
        try:
            move_image(src, dest)
            self.images.pop(self.current_index)
            if self.current_index >= len(self.images):
                self.current_index = max(0, len(self.images) - 1)
            if self.images:
                self.show_current()
            else:
                show_info("All photos have been sorted.")
                self.view.quit()
        except Exception as e:
            show_error(f"Failed to move file: {e}")    
    
    def reset_categories_and_source(self):
        """Reset only categories and last_folder, keep window_size."""
        self.config["categories"] = []
        self.config["last_folder"] = ""
        save_config(self.config)
        self.current_folder = None
        self.images = []
        self.current_index = 0
        self.build_category_buttons()
        self.view.show_image(None)
        self.view.update_status("Select a source folder.")

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
        # Destroy the window
        self.view.destroy()
