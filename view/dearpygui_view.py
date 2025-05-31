"""
DearPyGui implementation of the photo sorter UI.

This file defines the DearPyGuiView class, which provides a graphical user interface for the photo sorter application using the Dear PyGui library. It implements the BaseView interface, allowing the UI backend to be swapped if needed. The class manages the main application window, image display, category buttons, status updates, and user interactions such as folder selection, navigation, and category assignment. It also handles window geometry, keyboard shortcuts, and resource cleanup. The design aims for a clean, modern look and a responsive user experience.
"""
from pathlib import Path
import os  # Required for os.system in Open GitHub button
import dearpygui.dearpygui as dpg
from view.base_view import BaseView
import numpy as np
from PIL import Image
from typing import Optional, Callable, Union, Any, Dict, List

# Main DearPyGui-based view class for the photo sorter application
class DearPyGuiView(BaseView):
    def __init__(self):
        # Initialize Dear PyGui context and window properties
        dpg.create_context()
        self.width = 800
        self.height = 600
        self.x = 100
        self.y = 100

        # Set up fixed dimensions for the image display area
        self.image_display_width = 400
        self.image_display_height = 300
        
        # Create texture registry and image textures for displaying images
        with dpg.texture_registry() as self.texture_registry:
            self.placeholder_texture_tag = "placeholder_texture"
            dpg.add_dynamic_texture(
                width=1,
                height=1,
                default_value=[0.0, 0.0, 0.0, 0.0],
                tag=self.placeholder_texture_tag
            )
            self.image_texture_tag = "image_texture"
            initial_texture_data = [0.0] * (self.image_display_width * self.image_display_height * 4)
            dpg.add_dynamic_texture(
                width=self.image_display_width,
                height=self.image_display_height,
                default_value=initial_texture_data,
                tag=self.image_texture_tag
            )
        
        # Create the main application viewport and window
        icon_path = Path(__file__).parent.parent / "icon.ico"
        dpg.create_viewport(
            title="Photo Sorter",
            width=self.width,
            height=self.height,
            x_pos=self.x,
            y_pos=self.y,
            small_icon=str(icon_path),
            large_icon=str(icon_path)
        )
        dpg.setup_dearpygui()
        
        # Build the main window layout and UI controls
        with dpg.window(label="", tag="main_window", no_close=True, no_collapse=True, no_move=True, no_title_bar=True, no_resize=True, width=self.width, height=self.height, pos=[0,0]):
            # Add menu bar with About dialog
            with dpg.menu_bar():
                with dpg.menu(label="Menu"):
                    dpg.add_menu_item(label="About", callback=self.show_about_popup)
            # Add top controls for folder selection and reset
            dpg.add_group(horizontal=True, tag="top_controls")
            dpg.add_button(label="Select Folder", callback=self._on_select_folder, parent="top_controls")
            dpg.add_button(label="Reset", tag="reset_button", parent="top_controls")
            
            # Add status text for user feedback
            dpg.add_text("Select a source folder", tag="status_text")
            
            # Add image display area with navigation buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="<", callback=self._on_prev)
                dpg.add_image(texture_tag=self.image_texture_tag, tag="image_display", width=self.image_display_width, height=self.image_display_height)
                dpg.add_button(label=">", callback=self._on_next)
            
            # Add container for category buttons
            dpg.add_group(tag="categories_container")
        
        # Create the About popup window (hidden by default)
        with dpg.window(
            label="About",
            modal=True,
            show=False,
            tag="about_popup",
            no_close=True,
            no_collapse=True,
            no_move=True,
            width=360,
            height=150
        ):
            dpg.add_text("Photo Sorter")
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True):
                dpg.add_text("GitHub:")
                dpg.add_text(
                    "https://github.com/gorfreee/photo_sorter",
                    color=[0, 102, 204],
                    bullet=False,
                    tag="github_link",
                    show=True
                )
            dpg.add_spacer(height=2)
            dpg.add_text("License: MIT License")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=60)
                dpg.add_button(label="Open GitHub", width=120, callback=lambda: os.system('start https://github.com/gorfreee/photo_sorter'))
                dpg.add_spacer(width=10)
                dpg.add_button(label="Close", width=80, callback=lambda: dpg.configure_item("about_popup", show=False))

        # Initialize callback and state dictionaries
        self._callbacks: Dict[str, Callable] = {}
        self._category_callbacks: Dict[int, Dict[str, Callable]] = {}
        self._folder_path: Optional[str] = None
        self._exit_handler: Optional[Callable] = None
        
        # Show the application viewport
        dpg.show_viewport()

        # Set up viewport resize handling to keep the main window filling the viewport
        def _on_viewport_resize():
            vp_width = dpg.get_viewport_client_width()
            vp_height = dpg.get_viewport_client_height()
            self.width = vp_width
            self.height = vp_height
            dpg.configure_item("main_window", width=vp_width, height=vp_height, pos=[0, 0])
        dpg.set_viewport_resize_callback(_on_viewport_resize)
        _on_viewport_resize()

    # Internal event handler for folder selection button
    def _on_select_folder(self) -> None:
        if self._callbacks.get("select_folder"):
            self._callbacks["select_folder"]()

    # Internal event handler for next image button
    def _on_next(self) -> None:
        if self._callbacks.get("next"):
            self._callbacks["next"]()

    # Internal event handler for previous image button
    def _on_prev(self) -> None:
        if self._callbacks.get("prev"):
            self._callbacks["prev"]()

    # Get or set the window geometry (size and position)
    def geometry(self, new_geometry: Optional[str] = None) -> str:
        if new_geometry:
            try:
                parts = new_geometry.replace(" ", "").replace("+", "x+").split("+")
                parsed_w, parsed_h = self.width, self.height
                parsed_x, parsed_y = self.x, self.y
                if parts and parts[0]:
                    size_parts = parts[0].split("x")
                    if len(size_parts) == 2:
                        w_str, h_str = size_parts
                        if w_str: parsed_w = int(w_str)
                        if h_str: parsed_h = int(h_str)
                if len(parts) > 1 and parts[1]:
                    if parts[1]: parsed_x = int(parts[1])
                if len(parts) > 2 and parts[2]:
                    if parts[2]: parsed_y = int(parts[2])
                self.width, self.height = parsed_w, parsed_h
                self.x, self.y = parsed_x, parsed_y
            except ValueError:
                print(f"Warning: Could not parse geometry string '{new_geometry}'. Using current values.")
            current_x, current_y = dpg.get_viewport_pos() if dpg.is_dearpygui_running() else (100, 100)
            self.x = self.x if self.x is not None else current_x
            self.y = self.y if self.y is not None else current_y
            self.width = max(100, self.width if self.width is not None else 800)
            self.height = max(100, self.height if self.height is not None else 600)
            if dpg.is_dearpygui_running():
                dpg.set_viewport_pos([self.x, self.y])
                dpg.set_viewport_width(self.width)
                dpg.set_viewport_height(self.height)
                if dpg.does_item_exist("main_window"):
                    dpg.configure_item("main_window", width=self.width, height=self.height)
            else:
                pass
        return f"{self.width}x{self.height}+{self.x}+{self.y}"

    # Register a protocol callback (e.g., for window close events)
    def protocol(self, protocol_name: str, callback: Optional[Callable] = None) -> None:
        if protocol_name == "WM_DELETE_WINDOW" and callback:
            self._callbacks["close"] = callback

    # Register callback for folder selection
    def on_select_folder(self, callback: Callable) -> None:
        self._callbacks["select_folder"] = callback

    # Register callback for next image
    def on_next(self, callback: Callable) -> None:
        self._callbacks["next"] = callback

    # Register callback for previous image
    def on_prev(self, callback: Callable) -> None:
        self._callbacks["prev"] = callback

    # Register callback for reset button
    def add_reset_button(self, callback: Callable) -> None:
        self._callbacks["reset"] = callback
        dpg.set_item_callback("reset_button", self._on_reset)

    # Internal event handler for reset button
    def _on_reset(self) -> None:
        if self._callbacks.get("reset"):
            self._callbacks["reset"]()

    # Show a native folder selection dialog and return the selected path
    def ask_for_folder(self) -> str:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory(title="Select Source Folder")
        root.destroy()
        return folder_selected or ""

    # Display a PIL image in the DearPyGui window
    def show_image(self, photo: Optional[Image.Image]) -> None:
        FIXED_WIDTH, FIXED_HEIGHT = self.image_display_width, self.image_display_height
        if photo is None:
            if dpg.does_item_exist("image_display"):
                dpg.configure_item("image_display", texture_tag=self.placeholder_texture_tag, width=FIXED_WIDTH, height=FIXED_HEIGHT)
            return
        if photo.mode != "RGBA":
            photo = photo.convert("RGBA")
        if photo.size != (FIXED_WIDTH, FIXED_HEIGHT):
            photo = photo.resize((FIXED_WIDTH, FIXED_HEIGHT), Image.Resampling.LANCZOS)
        img_array = np.asarray(photo).astype(np.float32) / 255.0
        if img_array.ndim == 2:
            img_array = np.stack([img_array]*3 + [np.ones_like(img_array)], axis=-1)
        elif img_array.shape[2] == 3:
            alpha_channel = np.ones((img_array.shape[0], img_array.shape[1], 1), dtype=np.float32)
            img_array = np.concatenate((img_array, alpha_channel), axis=-1)
        elif img_array.shape[2] > 4:
            img_array = img_array[:, :, :4]
        if not img_array.flags['C_CONTIGUOUS']:
            img_array = np.ascontiguousarray(img_array)
        img_list = img_array.flatten().tolist()
        dpg.set_value(self.image_texture_tag, img_list)
        if dpg.does_item_exist("image_display"):
            dpg.configure_item("image_display", 
                               texture_tag=self.image_texture_tag, 
                               width=FIXED_WIDTH, 
                               height=FIXED_HEIGHT)
        dpg.set_item_label("image_display", f"{FIXED_WIDTH}x{FIXED_HEIGHT}")
    
    # Clean up DearPyGui resources and close the window
    def destroy(self) -> None:
        if self._callbacks.get("close"):
            self._callbacks["close"]()
        dpg.destroy_context()
    
    # Start the DearPyGui main loop
    def mainloop(self, n: int = 0, **kwargs) -> None:
        dpg.start_dearpygui()
    
    # Exit the application
    def quit(self) -> None:
        dpg.stop_dearpygui()
        self.destroy()
    
    # Get current window width
    def winfo_width(self) -> int:
        return int(dpg.get_viewport_width())
    
    # Get current window height
    def winfo_height(self) -> int:
        return int(dpg.get_viewport_height())
    
    # Get current window x position
    def winfo_x(self) -> int:
        return int(dpg.get_viewport_pos()[0])
    
    # Get current window y position
    def winfo_y(self) -> int:
        return int(dpg.get_viewport_pos()[1])
    
    # Update the status text in the UI
    def update_status(self, text: str, file_size_kb: Optional[float] = None) -> None:
        status = text
        if file_size_kb is not None:
            status += f" ({file_size_kb:.1f} KB)"
        dpg.set_value("status_text", status)
    
    # Set up category buttons for image sorting
    def set_categories(self, categories: List[Dict[str, str]]) -> None:
        if dpg.does_item_exist("categories_container"):
            dpg.delete_item("categories_container", children_only=True)
        self._category_callbacks.clear()
        for idx in range(9):
            cat = categories[idx] if idx < len(categories) else {"name": "", "path": ""}
            name = cat.get("name", "")
            button_text = f"{idx + 1}: {name}" if name else f"{idx + 1}: [Empty]"
            with dpg.group(parent="categories_container", horizontal=True):
                btn_id = dpg.generate_uuid()
                dpg.add_button(
                    label=button_text,
                    callback=lambda s, a, u: self._on_category_click(u),
                    user_data=idx,
                    width=200,
                    tag=btn_id
                )
                with dpg.item_handler_registry() as handler_id:
                    dpg.add_item_clicked_handler(
                        button=dpg.mvMouseButton_Right,
                        callback=lambda s, a, u: self._on_category_right_click(u),
                        user_data=idx
                    )
                dpg.bind_item_handler_registry(btn_id, handler_id)

    # Handle left-click on a category button
    def _on_category_click(self, idx: int) -> None:
        if idx in self._category_callbacks:
            self._category_callbacks[idx]["click"](idx)
    
    # Handle right-click on a category button
    def _on_category_right_click(self, idx: int) -> None:
        if idx in self._category_callbacks:
            self._category_callbacks[idx]["right"](idx)
    
    # Bind callbacks for category button clicks and right-clicks
    def bind_category(self, idx: int, on_click: Callable[[int], None], on_right_click: Callable[[int], None]) -> None:
        self._category_callbacks[idx] = {
            "click": on_click,
            "right": on_right_click
        }
    
    # Bind keyboard shortcuts for navigation and category selection
    def bind_keyboard_shortcuts(self) -> None:
        if hasattr(self, '_keyboard_handlers_registered') and self._keyboard_handlers_registered:
            return
        self._keyboard_handlers_registered = True
        with dpg.handler_registry():
            for i in range(9):
                dpg.add_key_press_handler(
                    dpg.mvKey_1 + i,
                    callback=lambda s, a, u: self._on_category_click(u),
                    user_data=i
                )
            dpg.add_key_press_handler(dpg.mvKey_Left, callback=lambda: self._on_prev())
            dpg.add_key_press_handler(dpg.mvKey_Right, callback=lambda: self._on_next())
    
    # Handle viewport resize events to keep the main window sized correctly
    def _on_viewport_resize(self) -> None:
        self.width = dpg.get_viewport_width()
        self.height = dpg.get_viewport_height()
        dpg.configure_item("main_window", width=self.width, height=self.height)

    # Utility to center a DearPyGui window in the viewport
    def _center_window(self, window_id: str, width: int, height: int) -> None:
        vp_width = dpg.get_viewport_client_width()
        vp_height = dpg.get_viewport_client_height()
        x = max((vp_width - width) // 2, 0)
        y = max((vp_height - height) // 2, 0)
        dpg.set_item_pos(window_id, [x, y])

    # Show the About popup window, centered in the viewport
    def show_about_popup(self, sender=None, app_data=None, user_data=None):
        self._center_window("about_popup", 400, 160)
        dpg.configure_item("about_popup", show=True)
