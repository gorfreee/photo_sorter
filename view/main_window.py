# main_window.py
# Defines the MainWindow class, which builds the main Tkinter UI for the app.
# This file contains all the code for the main window, keeping UI code organized and separate from logic and data.

import tkinter as tk
from tkinter import filedialog

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Photo Sorter')
        self.geometry('800x600')

        # Main layout
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        # Status label
        self.status_label = tk.Label(self.main_frame, text='Select a source folder.')
        self.status_label.pack(pady=20)

        # Image display
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(pady=10)
        self.prev_btn = tk.Button(nav_frame, text='Previous')
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn = tk.Button(nav_frame, text='Next')
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Folder selection
        self.select_btn = tk.Button(self.main_frame, text='Select a source folder')
        self.select_btn.pack(pady=10)

        # Category buttons frame
        self.cat_btn_frame = tk.Frame(self.main_frame)
        self.cat_btn_frame.pack(pady=10, fill='both', expand=True)
        self.cat_buttons = []
        
        # Store category callbacks for keyboard bindings
        self.category_click_callback = None
        self.category_right_callback = None
        
        # Track current button layout
        self.current_columns = 9
        
        # Bind window resize event
        self.bind('<Configure>', self._on_window_resize)

    def on_next(self, callback):
        self.next_btn.config(command=callback)

    def on_prev(self, callback):
        self.prev_btn.config(command=callback)

    def on_select_folder(self, callback):
        self.select_btn.config(command=callback)

    def ask_for_folder(self):
        return filedialog.askdirectory()

    def show_image(self, photo):
        if photo:
            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            self.image_label.config(image='')
            self.image_label.image = None

    def update_status(self, text):
        self.status_label.config(text=text)
        
    def set_categories(self, categories):
        # Remove old buttons
        for btn in self.cat_buttons:
            btn.destroy()
        self.cat_buttons.clear()
        
        # Create new buttons with dynamic layout
        self._rebuild_category_grid(categories, self.current_columns)

    def bind_category(self, idx, on_click, on_right_click):
        btn = self.cat_buttons[idx]
        btn.bind('<Button-1>', lambda e: on_click(idx))
        btn.bind('<Button-3>', lambda e: on_right_click(idx))
        
        # Store callbacks for keyboard bindings
        self.category_click_callback = on_click
        self.category_right_callback = on_right_click

    def bind_keyboard_shortcuts(self):
        # Bind keys 1-9 for category assignment
        for i in range(9):
            self.bind(str(i+1), lambda e, idx=i: self.category_click_callback(idx) if self.category_click_callback else None)
            
    def _rebuild_category_grid(self, categories, columns):
        """Rebuild the category grid with the specified number of columns"""
        # Reset all grid configurations
        for i in range(9):  # Max 9 categories
            self.cat_btn_frame.grid_columnconfigure(i, weight=0)
        
        # Configure grid weights for current columns
        for i in range(min(columns, 9)):  # Max 9 columns
            self.cat_btn_frame.grid_columnconfigure(i, weight=1)
            
        # Add buttons in a grid with calculated columns
        for i in range(9):  # Always 9 category buttons
            row = i // columns
            col = i % columns
            
            # Determine button text based on category configuration
            if i < len(categories) and categories[i].get('name') and categories[i].get('path'):
                btn_text = f'{i+1}: {categories[i]["name"]}'
            else:
                btn_text = f'{i+1}: Select a category'
                
            btn = tk.Button(self.cat_btn_frame, text=btn_text, width=18)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.cat_buttons.append(btn)
            
        # Configure row weights for responsive layout
        rows_needed = (9 + columns - 1) // columns  # Ceiling division
        for r in range(rows_needed):
            self.cat_btn_frame.grid_rowconfigure(r, weight=1)
            
    def _on_window_resize(self, event):
        """Handle window resize events to adjust button layout"""
        # Only respond to main window resize events, not child widget events
        if event.widget != self:
            return
            
        # Minimum width for a button
        min_btn_width = 110
        
        # Calculate available width (accounting for some padding)
        available_width = event.width - 40  # Subtract some padding
        
        # Calculate how many columns can fit
        columns = max(1, min(9, available_width // min_btn_width))
        
        # Only rebuild if the column count changed
        if columns != self.current_columns:
            self.current_columns = columns
            
            # Get current categories
            categories = []
            for i, btn in enumerate(self.cat_buttons):
                btn_text = btn.cget('text')
                if 'Select a category' not in btn_text:
                    name = btn_text[3:]  # Remove '1: ' prefix
                    categories.append({'name': name, 'path': ''})  # Path isn't visible in UI
                else:
                    categories.append({'name': '', 'path': ''})
            
            # Schedule rebuild to avoid flickering during resize
            self.after_idle(lambda: self.set_categories(categories))
