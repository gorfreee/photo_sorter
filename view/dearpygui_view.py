"""
DearPyGui implementation of the photo sorter UI.
Implements the BaseView interface for UI backend swapping.
"""
from pathlib import Path
import os  # Required for os.system in Open GitHub button
import dearpygui.dearpygui as dpg
from view.base_view import BaseView
import numpy as np
from PIL import Image
from typing import Optional, Callable, Union, Any, Dict, List

class DearPyGuiView(BaseView):
    def __init__(self):
        # Initialize DPG context
        dpg.create_context()
        
        # Initialize window size and position
        self.width = 800
        self.height = 600
        self.x = 100
        self.y = 100

        # Define fixed dimensions for the image display area
        self.image_display_width = 400
        self.image_display_height = 300
        
        # Create texture registry first
        with dpg.texture_registry() as self.texture_registry:
            # Create a 1x1 transparent RGBA texture as a placeholder
            self.placeholder_texture_tag = "placeholder_texture"
            dpg.add_dynamic_texture(
                width=1,
                height=1,
                default_value=[0.0, 0.0, 0.0, 0.0], # 1x1 transparent
                tag=self.placeholder_texture_tag
            )
            # Create a main image texture with fixed dimensions
            self.image_texture_tag = "image_texture"
            # Initial empty/transparent data for the fixed size texture
            initial_texture_data = [0.0] * (self.image_display_width * self.image_display_height * 4) # RGBA
            dpg.add_dynamic_texture(
                width=self.image_display_width,
                height=self.image_display_height,
                default_value=initial_texture_data,
                tag=self.image_texture_tag
            )
        
        # Create viewport and window
        dpg.create_viewport(title="Photo Sorter", width=self.width, height=self.height, x_pos=self.x, y_pos=self.y)
        dpg.setup_dearpygui()
        
        # Main window: remove title bar and borders for a clean look
        with dpg.window(label="", tag="main_window", no_close=True, no_collapse=True, no_move=True, no_title_bar=True, width=self.width, height=self.height, pos=[0,0]):
            # Add a menu bar integrated into the top
            with dpg.menu_bar():
                with dpg.menu(label="Menu"):
                    dpg.add_menu_item(label="About", callback=self.show_about_popup)
            # Create image display area and controls
            dpg.add_group(horizontal=True, tag="top_controls")
            dpg.add_button(label="Select Folder", callback=self._on_select_folder, parent="top_controls")
            dpg.add_button(label="Reset", tag="reset_button", parent="top_controls")
            
            # Status text
            dpg.add_text("Select a source folder", tag="status_text")
            
            # Image display group
            with dpg.group(horizontal=True):
                dpg.add_button(label="<", callback=self._on_prev)
                # Use the fixed dimensions for the image widget
                dpg.add_image(texture_tag=self.image_texture_tag, tag="image_display", width=self.image_display_width, height=self.image_display_height)
                dpg.add_button(label=">", callback=self._on_next)
            
            # Category buttons container
            dpg.add_group(tag="categories_container")
        
        # About popup (hidden by default)
        with dpg.window(
            label="About",
            modal=True,
            show=False,
            tag="about_popup",
            no_close=True,
            no_collapse=True,
            no_move=True,
            width=400,
            height=160
        ):
            dpg.add_text("Photo Sorter")
            dpg.add_spacer(height=2)
            # GitHub row
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
            # Centered row for buttons
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=60)  # left margin for centering
                dpg.add_button(label="Open GitHub", width=120, callback=lambda: os.system('start https://github.com/gorfreee/photo_sorter'))
                dpg.add_spacer(width=10)
                dpg.add_button(label="Close", width=80, callback=lambda: dpg.configure_item("about_popup", show=False))

        # Callbacks dictionary
        self._callbacks: Dict[str, Callable] = {}
        self._category_callbacks: Dict[int, Dict[str, Callable]] = {}
        self._folder_path: Optional[str] = None
        
        # Event handlers
        self._exit_handler: Optional[Callable] = None
        
        # Initial handler setups
        dpg.set_viewport_resize_callback(self._on_viewport_resize)
        
        # Start DPG
        dpg.show_viewport()

        # Ensure main window always fills the viewport on resize
        def update_main_window_size():
            win_width = dpg.get_viewport_width()
            win_height = dpg.get_viewport_height()
            dpg.configure_item("main_window", width=win_width, height=win_height)
        dpg.set_viewport_resize_callback(lambda: update_main_window_size())
        # Set initial size to fill viewport
        update_main_window_size()

    def _on_select_folder(self) -> None:
        """Internal handler for select folder button."""
        if self._callbacks.get("select_folder"):
            self._callbacks["select_folder"]()

    def _on_next(self) -> None:
        """Internal handler for next button."""
        if self._callbacks.get("next"):
            self._callbacks["next"]()

    def _on_prev(self) -> None:
        """Internal handler for previous button."""
        if self._callbacks.get("prev"):
            self._callbacks["prev"]()

    def geometry(self, new_geometry: Optional[str] = None) -> str:
        if new_geometry:
            try:
                parts = new_geometry.replace(" ", "").replace("+", "x+").split("+") # Normalize and split
                
                # Default to current values if parsing fails or parts are missing
                parsed_w, parsed_h = self.width, self.height
                parsed_x, parsed_y = self.x, self.y

                if parts and parts[0]: # Process width and height
                    size_parts = parts[0].split("x")
                    if len(size_parts) == 2:
                        w_str, h_str = size_parts
                        if w_str: parsed_w = int(w_str)
                        if h_str: parsed_h = int(h_str)
                
                if len(parts) > 1 and parts[1]: # Process x position
                    if parts[1]: parsed_x = int(parts[1])
                
                if len(parts) > 2 and parts[2]: # Process y position
                    if parts[2]: parsed_y = int(parts[2])

                self.width, self.height = parsed_w, parsed_h
                self.x, self.y = parsed_x, parsed_y

            except ValueError:
                # Log error or handle silently, falling back to current/default values
                # For example, you could use dpg.log_warning or print a message
                print(f"Warning: Could not parse geometry string '{new_geometry}'. Using current values.")
                # self.width, self.height, self.x, self.y remain unchanged or use defaults
            
            # Apply to DPG, ensuring minimum reasonable size and valid positions
            # Ensure x and y are not None before using them
            current_x, current_y = dpg.get_viewport_pos() if dpg.is_dearpygui_running() else (100, 100)
            self.x = self.x if self.x is not None else current_x
            self.y = self.y if self.y is not None else current_y
            
            # Ensure width and height are reasonable
            self.width = max(100, self.width if self.width is not None else 800)
            self.height = max(100, self.height if self.height is not None else 600)

            if dpg.is_dearpygui_running():
                dpg.set_viewport_pos([self.x, self.y])
                dpg.set_viewport_width(self.width)
                dpg.set_viewport_height(self.height)
                # Update main window size
                if dpg.does_item_exist("main_window"):
                    dpg.configure_item("main_window", width=self.width, height=self.height)
            else:
                # If DPG is not running (e.g. during init before start_dearpygui),
                # these values will be used when dpg.create_viewport is called.
                pass
                
        return f"{self.width}x{self.height}+{self.x}+{self.y}"

    def protocol(self, protocol_name: str, callback: Optional[Callable] = None) -> None:
        if protocol_name == "WM_DELETE_WINDOW" and callback:
            self._callbacks["close"] = callback

    def on_select_folder(self, callback: Callable) -> None:
        self._callbacks["select_folder"] = callback

    def on_next(self, callback: Callable) -> None:
        self._callbacks["next"] = callback

    def on_prev(self, callback: Callable) -> None:
        self._callbacks["prev"] = callback

    def add_reset_button(self, callback: Callable) -> None:
        self._callbacks["reset"] = callback
        dpg.set_item_callback("reset_button", self._on_reset)

    def _on_reset(self) -> None:
        if self._callbacks.get("reset"):
            self._callbacks["reset"]()

    def ask_for_folder(self) -> str:
        # Use native Windows folder selection dialog via tkinter
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        folder_selected = filedialog.askdirectory(title="Select Source Folder")
        root.destroy()
        return folder_selected or ""

    def show_image(self, photo: Optional[Image.Image]) -> None:
        """Display the given PIL image in the DearPyGui window."""
        # Use the fixed dimensions defined in __init__
        FIXED_WIDTH, FIXED_HEIGHT = self.image_display_width, self.image_display_height
        
        if photo is None:
            if dpg.does_item_exist("image_display"):
                # Switch the image widget to display the placeholder texture
                dpg.configure_item("image_display", texture_tag=self.placeholder_texture_tag, width=FIXED_WIDTH, height=FIXED_HEIGHT)
            # Do not modify self.image_texture_tag here, as it's fixed size and holds last image or initial data.
            # If you want to clear it to transparent when no image, you can set its value to transparent data:
            # transparent_data = [0.0] * (FIXED_WIDTH * FIXED_HEIGHT * 4)
            # dpg.set_value(self.image_texture_tag, transparent_data)
            # For now, we'll let it show the last valid image or its initial state.
            return

        # Always convert to RGBA for DearPyGui
        if photo.mode != "RGBA":
            photo = photo.convert("RGBA")
        
        # Resize to fixed display dimensions if not already (model.create_thumbnail should handle this)
        if photo.size != (FIXED_WIDTH, FIXED_HEIGHT):
            photo = photo.resize((FIXED_WIDTH, FIXED_HEIGHT), Image.Resampling.LANCZOS)
            
        img_array = np.asarray(photo).astype(np.float32) / 255.0  # Normalize to [0,1]
        
        # Ensure 4 channels (RGBA)
        if img_array.ndim == 2: # Grayscale
            # Convert to RGBA: R=G=B=grayscale_value, A=1.0
            img_array = np.stack([img_array]*3 + [np.ones_like(img_array)], axis=-1)
        elif img_array.shape[2] == 3: # RGB
            # Add alpha channel (fully opaque)
            alpha_channel = np.ones((img_array.shape[0], img_array.shape[1], 1), dtype=np.float32)
            img_array = np.concatenate((img_array, alpha_channel), axis=-1)
        elif img_array.shape[2] > 4: # More than 4 channels
            img_array = img_array[:, :, :4] # Keep only the first 4 (RGBA)

        # Ensure the array is C-contiguous for DearPyGui
        if not img_array.flags['C_CONTIGUOUS']:
            img_array = np.ascontiguousarray(img_array)

        img_list = img_array.flatten().tolist()

        # Update the existing dynamic texture (which is already FIXED_WIDTH x FIXED_HEIGHT)
        dpg.set_value(self.image_texture_tag, img_list)
        
        # Ensure the image_display widget uses the main image_texture_tag
        # and its dimensions are correctly set (they match FIXED_WIDTH, FIXED_HEIGHT).
        if dpg.does_item_exist("image_display"):
            dpg.configure_item("image_display", 
                               texture_tag=self.image_texture_tag, 
                               width=FIXED_WIDTH, 
                               height=FIXED_HEIGHT)
        dpg.set_item_label("image_display", f"{FIXED_WIDTH}x{FIXED_HEIGHT}")  # Optional: show size for debug
    
    def destroy(self) -> None:
        """Clean up DPG resources and close the window."""
        if self._callbacks.get("close"):
            self._callbacks["close"]()
        dpg.destroy_context()
    
    def mainloop(self, n: int = 0, **kwargs) -> None: # Added n and **kwargs to match base
        """Start the Dear PyGui main loop."""
        dpg.start_dearpygui()
    
    def quit(self) -> None:
        """Exit the application."""
        dpg.stop_dearpygui()
        self.destroy()
    
    def winfo_width(self) -> int:
        """Get current window width."""
        return int(dpg.get_viewport_width())
    
    def winfo_height(self) -> int:
        """Get current window height."""
        return int(dpg.get_viewport_height())
    
    def winfo_x(self) -> int:
        """Get current window x position."""
        return int(dpg.get_viewport_pos()[0])
    
    def winfo_y(self) -> int:
        """Get current window y position."""
        return int(dpg.get_viewport_pos()[1])
    
    def update_status(self, text: str, file_size_kb: Optional[float] = None) -> None:
        """Update the status text."""
        status = text
        if file_size_kb is not None:
            status += f" ({file_size_kb:.1f} KB)"
        dpg.set_value("status_text", status)
    
    def set_categories(self, categories: List[Dict[str, str]]) -> None:
        """Set up category buttons."""
        if dpg.does_item_exist("categories_container"):
            dpg.delete_item("categories_container", children_only=True)
        self._category_callbacks.clear()  # Clear old callbacks to prevent duplication
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
                # Add right-click handler
                with dpg.item_handler_registry() as handler_id:
                    dpg.add_item_clicked_handler(
                        button=dpg.mvMouseButton_Right,
                        callback=lambda s, a, u: self._on_category_right_click(u),
                        user_data=idx
                    )
                dpg.bind_item_handler_registry(btn_id, handler_id)

    def _on_category_click(self, idx: int) -> None:
        """Handle category button clicks."""
        if idx in self._category_callbacks:
            self._category_callbacks[idx]["click"](idx)
    
    def _on_category_right_click(self, idx: int) -> None:
        """Handle right-click on category button."""
        if idx in self._category_callbacks:
            self._category_callbacks[idx]["right"](idx)
    
    def bind_category(self, idx: int, on_click: Callable[[int], None], on_right_click: Callable[[int], None]) -> None:
        """Bind category button callbacks."""
        self._category_callbacks[idx] = {
            "click": on_click,
            "right": on_right_click
        }
    
    def bind_keyboard_shortcuts(self) -> None:
        """Bind keyboard shortcuts only once."""
        if hasattr(self, '_keyboard_handlers_registered') and self._keyboard_handlers_registered:
            return
        self._keyboard_handlers_registered = True
        with dpg.handler_registry():
            # Numeric keys for categories
            for i in range(9):
                dpg.add_key_press_handler(
                    dpg.mvKey_1 + i,
                    callback=lambda s, a, u: self._on_category_click(u),
                    user_data=i
                )
            # Arrow keys for navigation
            dpg.add_key_press_handler(dpg.mvKey_Left, callback=lambda: self._on_prev())
            dpg.add_key_press_handler(dpg.mvKey_Right, callback=lambda: self._on_next())
    
    def _on_viewport_resize(self) -> None:
        """Handle viewport resize events."""
        self.width = dpg.get_viewport_width()
        self.height = dpg.get_viewport_height()
        dpg.configure_item("main_window", width=self.width, height=self.height)

    def show_about_popup(self, sender, app_data, user_data=None):
        # Center the popup in the viewport
        vp_width, vp_height = dpg.get_viewport_client_width(), dpg.get_viewport_client_height()
        popup_width, popup_height = 400, 220
        dpg.set_item_pos("about_popup", [
            (vp_width - popup_width) // 2,
            (vp_height - popup_height) // 2
        ])
        dpg.configure_item("about_popup", show=True)
