"""
DearPyGui implementation of the photo sorter UI.

This file defines the DearPyGuiView class, which provides a graphical user interface for the photo sorter application using the Dear PyGui library. It implements the BaseView interface, allowing the UI backend to be swapped if needed. The class manages the main application window, image display, category buttons, status updates, and user interactions such as folder selection, navigation, and category assignment. The design aims for a clean, modern look and a responsive user experience.
"""
from pathlib import Path
import os
import webbrowser
import dearpygui.dearpygui as dpg
from view.base_view import BaseView
import numpy as np
from PIL import Image
from typing import Optional, Callable, Union, Any, Dict, List
import threading

# Main DearPyGui-based view class for the photo sorter application
class DearPyGuiView(BaseView):
    _instance = None  # Singleton instance for global access

    # --- UI Tags and Layout Parameters ---
    TAG_MAIN_WINDOW = "main_window"
    TAG_MENU_BAR = "menu_bar"
    TAG_TOP_CONTROLS = "top_controls"
    TAG_RESET_BUTTON = "reset_button"
    TAG_STATUS_TEXT = "status_text"
    TAG_IMAGE_DISPLAY = "image_display"
    TAG_IMAGE_TEXTURE = "image_texture"
    TAG_PLACEHOLDER_TEXTURE = "placeholder_texture"
    TAG_IMAGE_AREA = "image_area_group"
    TAG_PREV_BUTTON = "prev_button"
    TAG_NEXT_BUTTON = "next_button"
    TAG_CATEGORIES_CONTAINER = "categories_container"
    TAG_ABOUT_POPUP = "about_popup"
    TAG_GITHUB_LINK = "github_link"

    # Layout parameters
    DEFAULT_WIDTH = 900
    DEFAULT_HEIGHT = 650
    IMAGE_DISPLAY_WIDTH = 400
    IMAGE_DISPLAY_HEIGHT = 300
    CATEGORY_BUTTON_WIDTH = 200
    ABOUT_POPUP_WIDTH = 360
    ABOUT_POPUP_HEIGHT = 150

    def __init__(self):
        DearPyGuiView._instance = self  # Set singleton instance
        # --- Initialize Dear PyGui context and compute viewport position/size ---
        dpg.create_context()
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT

        # Compute centered position for the viewport on the primary monitor
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            x_pos = max((screen_width - self.width) // 2, 0)
            y_pos = max((screen_height - self.height) // 2, 0)
        except Exception:
            x_pos, y_pos = 0, 0

        icon_path = Path(__file__).parent.parent / "icon.ico"
        # --- Store viewport parameters for later creation ---
        self._viewport_params = {
            "title": "Photo Sorter",
            "width": self.width,
            "height": self.height,
            "small_icon": str(icon_path),
            "large_icon": str(icon_path),
            "x_pos": x_pos,
            "y_pos": y_pos
        }

        # Create and configure the viewport before building UI to avoid blank initial frame
        dpg.create_viewport(**self._viewport_params)
        dpg.setup_dearpygui()

        # --- Build all UI widgets and windows, with viewport parameters ready ---
        with dpg.texture_registry() as self.texture_registry:
            dpg.add_dynamic_texture(
                width=1,
                height=1,
                default_value=[0.0, 0.0, 0.0, 0.0],
                tag=self.TAG_PLACEHOLDER_TEXTURE
            )
            initial_texture_data = [0.0] * (self.IMAGE_DISPLAY_WIDTH * self.IMAGE_DISPLAY_HEIGHT * 4)
            dpg.add_dynamic_texture(
                width=self.IMAGE_DISPLAY_WIDTH,
                height=self.IMAGE_DISPLAY_HEIGHT,
                default_value=initial_texture_data,
                tag=self.TAG_IMAGE_TEXTURE
            )

        # --- Modern Button Theme ---
        with dpg.theme() as self._button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [40, 120, 220, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [60, 140, 240, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [30, 100, 180, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
        # --- Active Button Theme for Visual Feedback ---
        with dpg.theme() as self._button_active_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [30, 100, 180, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [30, 100, 180, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [30, 100, 180, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
        self._category_button_ids = dict()
        self._feedback_timers = dict()
        self._nav_button_ids = dict()

        # --- Modern, Centered Layout ---
        with dpg.window(label="", tag=self.TAG_MAIN_WINDOW, no_close=True, no_collapse=True, no_move=True, no_title_bar=True, no_resize=True, width=self.width, height=self.height, pos=[0,0]):
            self._build_menu_bar()
            btn_reset = dpg.add_button(label="Reset", tag=self.TAG_RESET_BUTTON, pos=[self.width-70, 30])
            dpg.bind_item_theme(btn_reset, self._button_theme)
            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=0, tag="left_spacer")
                with dpg.group(tag="center_content"):
                    self._build_top_controls()
                    dpg.add_spacer(height=10)
                    self._build_status_text()
                    dpg.add_spacer(height=20)
                    self._build_image_area()
                    dpg.add_spacer(height=20)
                    self._build_categories_container()
                dpg.add_spacer(width=0, tag="right_spacer")
            dpg.add_spacer(height=20)
        self._build_about_popup()

        # Responsive centering on resize
        def _on_viewport_resize():
            vp_width = dpg.get_viewport_client_width()
            content_width = 2 * 40 + self.IMAGE_DISPLAY_WIDTH + 120
            side_space = max((vp_width - content_width) // 2, 0)
            dpg.configure_item("left_spacer", width=side_space)
            dpg.configure_item("right_spacer", width=side_space)
            dpg.configure_item(self.TAG_MAIN_WINDOW, width=vp_width, height=dpg.get_viewport_client_height(), pos=[0, 0])
            dpg.configure_item(self.TAG_RESET_BUTTON, pos=[vp_width-70, 30])
        dpg.set_viewport_resize_callback(_on_viewport_resize)

        # (moved to mainloop to show after everything is built)

        self._callbacks: Dict[str, Callable] = {}
        self._category_callbacks: Dict[int, Dict[str, Callable]] = {}
        self._folder_path: Optional[str] = None
        self._exit_handler: Optional[Callable] = None
        self._modal_open = False  # Track if a modal dialog is open

    # --- Modular UI Construction ---
    def _build_menu_bar(self):
        with dpg.menu_bar(tag=self.TAG_MENU_BAR):
            with dpg.menu(label="Menu"):
                dpg.add_menu_item(label="About", callback=self.show_about_popup)

    def _build_top_controls(self):
        with dpg.group(horizontal=True, tag=self.TAG_TOP_CONTROLS):
            btn1 = dpg.add_button(label="Select Source Folder", callback=self._on_select_folder, tag="select_folder_button")
            dpg.bind_item_theme(btn1, self._button_theme)
            # Add a text widget to display the selected folder path
            dpg.add_spacer(width=10)
            dpg.add_text("No folder selected", tag="selected_folder_path", wrap=400)

    def _build_status_text(self):
        dpg.add_text("Select a source folder", tag=self.TAG_STATUS_TEXT)

    def _build_image_area(self):
        with dpg.group(horizontal=True, tag=self.TAG_IMAGE_AREA):
            btn_prev = dpg.add_button(label="<", callback=self._on_prev, tag=self.TAG_PREV_BUTTON, width=40, height=self.IMAGE_DISPLAY_HEIGHT)
            dpg.bind_item_theme(btn_prev, self._button_theme)
            self._nav_button_ids['prev'] = btn_prev
            dpg.add_spacer(width=10)
            dpg.add_image(texture_tag=self.TAG_IMAGE_TEXTURE, tag=self.TAG_IMAGE_DISPLAY, width=self.IMAGE_DISPLAY_WIDTH, height=self.IMAGE_DISPLAY_HEIGHT)
            dpg.add_spacer(width=10)
            btn_next = dpg.add_button(label=">", callback=self._on_next, tag=self.TAG_NEXT_BUTTON, width=40, height=self.IMAGE_DISPLAY_HEIGHT)
            dpg.bind_item_theme(btn_next, self._button_theme)
            self._nav_button_ids['next'] = btn_next

    def _build_categories_container(self):
        dpg.add_group(tag=self.TAG_CATEGORIES_CONTAINER)

    def _build_about_popup(self):
        with dpg.window(
            label="About",
            modal=True,
            show=False,
            tag=self.TAG_ABOUT_POPUP,
            no_close=True,
            no_collapse=True,
            no_move=True,
            width=self.ABOUT_POPUP_WIDTH,
            height=self.ABOUT_POPUP_HEIGHT,
            no_resize=True  # Make the About popup non-resizable
        ):
            dpg.add_text("Photo Sorter")
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True):
                dpg.add_text("GitHub:")
                dpg.add_text(
                    "https://github.com/gorfreee/photo_sorter",
                    color=[0, 102, 204],
                    bullet=False,
                    tag=self.TAG_GITHUB_LINK,
                    show=True
                )
            dpg.add_spacer(height=2)
            dpg.add_text("License: MIT License")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=60)
                dpg.add_button(label="Open GitHub", width=120, callback=lambda: webbrowser.open('https://github.com/gorfreee/photo_sorter'))
                dpg.add_spacer(width=10)
                dpg.add_button(label="Close", width=80, callback=lambda: dpg.configure_item(self.TAG_ABOUT_POPUP, show=False))

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
        FIXED_WIDTH, FIXED_HEIGHT = self.IMAGE_DISPLAY_WIDTH, self.IMAGE_DISPLAY_HEIGHT
        if photo is None:
            if dpg.does_item_exist(self.TAG_IMAGE_DISPLAY):
                dpg.configure_item(self.TAG_IMAGE_DISPLAY, texture_tag=self.TAG_PLACEHOLDER_TEXTURE, width=FIXED_WIDTH, height=FIXED_HEIGHT)
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
        dpg.set_value(self.TAG_IMAGE_TEXTURE, img_list)
        if dpg.does_item_exist(self.TAG_IMAGE_DISPLAY):
            dpg.configure_item(self.TAG_IMAGE_DISPLAY, 
                               texture_tag=self.TAG_IMAGE_TEXTURE, 
                               width=FIXED_WIDTH, 
                               height=FIXED_HEIGHT)
        dpg.set_item_label(self.TAG_IMAGE_DISPLAY, f"{FIXED_WIDTH}x{FIXED_HEIGHT}")
    
    # Clean up DearPyGui resources and close the window
    def destroy(self) -> None:
        if self._callbacks.get("close"):
            self._callbacks["close"]()
        dpg.destroy_context()
    
    # Start the DearPyGui main loop
    def mainloop(self, n: int = 0, **kwargs) -> None:
        # Show the viewport now that UI is fully constructed and positioned
        dpg.show_viewport()
        # Start the DearPyGui main loop
        dpg.start_dearpygui()
    
    # Exit the application
    def quit(self) -> None:
        dpg.stop_dearpygui()
        self.destroy()
    
    # Update the status text in the UI
    def update_status(self, text: str, file_size_kb: Optional[float] = None) -> None:
        status = text
        if file_size_kb is not None:
            status += f" ({file_size_kb:.1f} KB)"
        dpg.set_value("status_text", status)
    
    # Helper function to create a single category button with all handlers, theme, and tooltip
    def _create_category_button(self, idx: int, cat: Dict[str, str], parent: str) -> None:
        name = cat.get("name", "")
        button_text = f"{idx + 1}: {name}" if name else f"{idx + 1}: [Empty]"
        btn_id = dpg.generate_uuid()
        btn = dpg.add_button(
            label=button_text,
            callback=lambda s, a, u: self._on_category_click(u),
            user_data=idx,
            width=self.CATEGORY_BUTTON_WIDTH,
            tag=btn_id,
            parent=str(parent)
        )
        dpg.bind_item_theme(btn, self._button_theme)
        # Store button ID for visual feedback
        if hasattr(self, '_category_button_ids'):
            self._category_button_ids[idx] = btn_id
        # Add tooltip if category has a name or path
        if name or cat.get("path"):
            with dpg.tooltip(btn_id):
                dpg.add_text(cat.get("path", ""))
        # Add right-click handler
        with dpg.item_handler_registry() as handler_id:
            dpg.add_item_clicked_handler(
                button=dpg.mvMouseButton_Right,
                callback=lambda s, a, u: self._on_category_right_click(u),
                user_data=idx
            )
        dpg.bind_item_handler_registry(btn_id, handler_id)

    # Set up category buttons for image sorting
    def set_categories(self, categories: List[Dict[str, str]]) -> None:
        if dpg.does_item_exist(self.TAG_CATEGORIES_CONTAINER):
            dpg.delete_item(self.TAG_CATEGORIES_CONTAINER, children_only=True)
        self._category_callbacks.clear()
        if hasattr(self, '_category_button_ids'):
            self._category_button_ids.clear()  # Clear button IDs when rebuilding
        # Arrange buttons in a 3x3 grid (3 rows, 3 buttons per row)
        for row in range(3):
            group_id = str(dpg.generate_uuid())
            with dpg.group(parent=self.TAG_CATEGORIES_CONTAINER, horizontal=True, tag=group_id):
                pass  # Just to create the group and get its tag
            for col in range(3):
                idx = row * 3 + col
                cat = categories[idx] if idx < len(categories) else {"name": "", "path": ""}
                self._create_category_button(idx, cat, group_id)

    # Handle left-click on a category button
    def _on_category_click(self, idx: int) -> None:
        import inspect
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back if frame else None
            if caller_frame and 'key_press_handler' in str(getattr(caller_frame.f_code, 'co_name', '')):
                # Use the method directly, not via hasattr
                DearPyGuiView._show_button_feedback(self, idx)
        finally:
            del frame
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
                    callback=lambda s, a, u: self._handle_keyboard_category(u),
                    user_data=i
                )
            dpg.add_key_press_handler(dpg.mvKey_Left, callback=self._handle_keyboard_prev)
            dpg.add_key_press_handler(dpg.mvKey_Right, callback=self._handle_keyboard_next)

    def _handle_keyboard_prev(self):
        self._show_nav_button_feedback('prev')
        self._on_prev()

    def _handle_keyboard_next(self):
        self._show_nav_button_feedback('next')
        self._on_next()

    def _handle_keyboard_category(self, idx: int) -> None:
        # Only trigger shortcut if no modal is open
        if getattr(self, "_modal_open", False):
            return
        DearPyGuiView._show_button_feedback(self, idx)
        self._on_category_click(idx)

    # Handle viewport resize events to keep the main window sized correctly
    def _on_viewport_resize(self) -> None:
        self.width = dpg.get_viewport_width()
        self.height = dpg.get_viewport_height()
        dpg.configure_item(self.TAG_MAIN_WINDOW, width=self.width, height=self.height)

    # Utility to center a DearPyGui window in the viewport
    def _center_window(self, window_id: str, width: int, height: int) -> None:
        vp_width = dpg.get_viewport_client_width()
        vp_height = dpg.get_viewport_client_height()
        x = max((vp_width - width) // 2, 0)
        y = max((vp_height - height) // 2, 0)
        dpg.set_item_pos(window_id, [x, y])

    # Show the About popup window, centered in the viewport
    def show_about_popup(self, sender=None, app_data=None, user_data=None):
        self._center_window(self.TAG_ABOUT_POPUP, 400, 160)
        dpg.configure_item(self.TAG_ABOUT_POPUP, show=True)

    def update_select_folder_button(self, folder_selected: bool) -> None:
        """Update the select folder button label based on selection state."""
        label = "Change Source Folder" if folder_selected else "Select Source Folder"
        if dpg.does_item_exist("select_folder_button"):
            dpg.set_item_label("select_folder_button", label)

    def set_selected_folder_path(self, folder_path: str) -> None:
        """Update the displayed selected folder path next to the Select Folder button."""
        if not folder_path:
            dpg.set_value("selected_folder_path", "No folder selected")
            self.update_select_folder_button(False)
        else:
            # Always display with OS-native separators
            import os
            folder_path = os.path.normpath(folder_path)
            dpg.set_value("selected_folder_path", folder_path)
            self.update_select_folder_button(True)

    # --- Visual Feedback for Category Buttons (Keyboard Shortcut) ---
    def _show_button_feedback(self, idx: int, duration: float = 0.05) -> None:
        """Show visual feedback for a category button by temporarily changing its theme."""
        if not hasattr(self, '_category_button_ids') or idx not in self._category_button_ids:
            return
        button_id = self._category_button_ids[idx]
        # Cancel any existing timer for this button
        if hasattr(self, '_feedback_timers') and idx in self._feedback_timers:
            self._feedback_timers[idx] = None
        dpg.bind_item_theme(button_id, self._button_active_theme)
        def restore_theme():
            if self._feedback_timers.get(idx) is not None:
                dpg.bind_item_theme(button_id, self._button_theme)
                if idx in self._feedback_timers:
                    del self._feedback_timers[idx]
        self._feedback_timers[idx] = True
        threading.Timer(duration, restore_theme).start()

    # --- Visual Feedback for Navigation Buttons (Keyboard Shortcut) ---
    def _show_nav_button_feedback(self, which: str, duration: float = 0.05) -> None:
        """Show visual feedback for a navigation button by temporarily changing its theme."""
        if which not in self._nav_button_ids:
            return
        button_id = self._nav_button_ids[which]
        # Cancel any existing timer for this button
        if not hasattr(self, '_feedback_timers'):
            self._feedback_timers = dict()
        nav_key = f'nav_{which}'
        if nav_key in self._feedback_timers:
            self._feedback_timers[nav_key] = None
        dpg.bind_item_theme(button_id, self._button_active_theme)
        def restore_theme():
            if self._feedback_timers.get(nav_key) is not None:
                dpg.bind_item_theme(button_id, self._button_theme)
                if nav_key in self._feedback_timers:
                    del self._feedback_timers[nav_key]
        self._feedback_timers[nav_key] = True
        threading.Timer(duration, restore_theme).start()

    def set_modal_open(self, is_open: bool):
        """Set the modal open state (True if a modal dialog is open)."""
        self._modal_open = is_open
