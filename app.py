"""
Photo Sorter App
A lightweight desktop app to sort photos into folders.
Uses Tkinter for the UI (no extra dependencies required).
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"categories": []}

# Save configuration to file
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# Main application class
def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Photo Sorter")
    root.geometry("800x600")

    # --- Layout Refactor: Use a main vertical frame for all content ---
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    label = tk.Label(main_frame, text="Select a source folder.")
    label.pack(pady=20)

    image_label = tk.Label(main_frame)
    image_label.pack(pady=10)

    images = []  # List of image file paths
    current_index = [0]  # Mutable index for navigation
    current_folder = [None]
    config = load_config()

    def load_images(folder):
        # Load supported image files from the folder
        supported = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        return [os.path.join(folder, f) for f in os.listdir(folder)
                if f.lower().endswith(supported)]

    def show_image():
        # Display the current image
        if images:
            img_path = images[current_index[0]]
            try:
                img = Image.open(img_path)
                img.thumbnail((600, 400))
                photo = ImageTk.PhotoImage(img)
                image_label.config(image=photo)
                image_label.image = photo  # Keep reference
                label.config(text=f"{os.path.basename(img_path)} ({current_index[0]+1}/{len(images)})")
            except Exception as e:
                label.config(text=f"Error loading image: {e}")
        else:
            image_label.config(image='')
            label.config(text="No images found.")

    def select_folder():
        folder = filedialog.askdirectory()
        if folder:
            current_folder[0] = folder
            label.config(text=f"Selected folder: {folder}")
            # No need for 'nonlocal images' here; just update the list in place
            images.clear()
            images.extend(load_images(folder))
            current_index[0] = 0
            show_image()

    def next_image():
        if images and current_index[0] < len(images) - 1:
            current_index[0] += 1
            show_image()

    def prev_image():
        if images and current_index[0] > 0:
            current_index[0] -= 1
            show_image()

    nav_frame = tk.Frame(main_frame)
    nav_frame.pack(pady=10)
    prev_btn = tk.Button(nav_frame, text="Previous", command=prev_image)
    prev_btn.pack(side=tk.LEFT, padx=5)
    next_btn = tk.Button(nav_frame, text="Next", command=next_image)
    next_btn.pack(side=tk.LEFT, padx=5)

    select_btn = tk.Button(main_frame, text="Select a source folder", command=select_folder)
    select_btn.pack(pady=10)

    # --- Category Buttons UI (9 placeholders) ---
    cat_btn_frame = tk.Frame(main_frame)
    cat_btn_frame.pack(pady=10)
    cat_buttons = []
    max_categories = 9

    def configure_category(idx):
        # Dialog to set or edit category name and path, or delete
        def save_and_close():
            name = name_var.get().strip()
            path = path_var.get().strip()
            if name and path:
                while len(config["categories"]) <= idx:
                    config["categories"].append({"name": "", "path": ""})
                config["categories"][idx]["name"] = name
                config["categories"][idx]["path"] = path
                save_config(config)
                build_category_buttons()
                dialog.destroy()
            else:
                messagebox.showwarning("Input required", "Please enter both a name and a folder.")
        def delete_and_close():
            if idx < len(config["categories"]):
                config["categories"][idx] = {"name": "", "path": ""}
                save_config(config)
                build_category_buttons()
            dialog.destroy()
        dialog = tk.Toplevel(root)
        dialog.title(f"Edit Category {idx+1}")
        dialog.grab_set()
        tk.Label(dialog, text=f"Category {idx+1} Name:").pack(padx=10, pady=5)
        name_var = tk.StringVar()
        path_var = tk.StringVar()
        if idx < len(config["categories"]):
            name_var.set(config["categories"][idx]["name"])
            path_var.set(config["categories"][idx]["path"])
        name_entry = tk.Entry(dialog, textvariable=name_var, width=20)
        name_entry.pack(padx=10, pady=2)
        tk.Label(dialog, text="Destination Folder:").pack(padx=10, pady=5)
        path_entry = tk.Entry(dialog, textvariable=path_var, width=30)
        path_entry.pack(padx=10, pady=2, side=tk.LEFT)
        def browse():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)
        browse_btn = tk.Button(dialog, text="...", command=browse)
        browse_btn.pack(padx=5, pady=2, side=tk.LEFT)
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        save_btn = tk.Button(btn_frame, text="Save", command=save_and_close)
        save_btn.pack(side=tk.LEFT, padx=5)
        del_btn = tk.Button(btn_frame, text="Delete", command=delete_and_close)
        del_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def assign_category(idx):
        if not images or idx >= len(config["categories"]):
            return
        cat = config["categories"][idx]
        dest_folder = cat["path"]
        src = images[current_index[0]]
        try:
            shutil.move(src, dest_folder)
            images.pop(current_index[0])
            if current_index[0] >= len(images):
                current_index[0] = max(0, len(images) - 1)
            if images:
                show_image()
            else:
                messagebox.showinfo("Done", "All photos have been sorted.")
                root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file: {e}")

    def on_cat_btn(event, idx):
        if event.num == 3:  # Right-click
            configure_category(idx)
        elif event.num == 1:  # Left-click
            if idx < len(config["categories"]) and config["categories"][idx]["name"] and config["categories"][idx]["path"]:
                assign_category(idx)
            else:
                configure_category(idx)

    last_columns = [9]  # Use a mutable object to track last used columns

    def build_category_buttons(columns=9):
        # Remove old buttons
        for btn in cat_buttons:
            btn.destroy()
        cat_buttons.clear()
        # Reset all previous column configs (up to max_categories)
        for i in range(max_categories):
            cat_btn_frame.grid_columnconfigure(i, weight=0)
        # Configure grid weights for current columns
        for i in range(columns):
            cat_btn_frame.grid_columnconfigure(i, weight=1)
        # Add buttons in a grid with calculated columns
        for i in range(max_categories):
            row = i // columns
            col = i % columns
            if i < len(config["categories"]) and config["categories"][i]["name"] and config["categories"][i]["path"]:
                btn_text = f"{i+1}: {config['categories'][i]['name']}"
            else:
                btn_text = f"{i+1}: Select a category"
            btn = tk.Button(cat_btn_frame, text=btn_text, width=18)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            btn.bind('<Button-1>', lambda e, idx=i: on_cat_btn(e, idx))
            btn.bind('<Button-3>', lambda e, idx=i: on_cat_btn(e, idx))
            cat_buttons.append(btn)
        # Bind keys 1-9
        for i in range(9):
            root.bind(str(i+1), lambda e, idx=i: assign_category(idx))
        last_columns[0] = columns

    def on_resize(event=None):
        min_btn_width = 110
        # Use root.winfo_width() for more reliable width
        frame_width = root.winfo_width()
        columns = max(1, min(max_categories, frame_width // min_btn_width))
        if columns != last_columns[0]:
            build_category_buttons(columns)

    # Build category buttons on startup
    build_category_buttons()
    # Bind resize event to reorganize buttons, using after_idle to avoid flicker
    def schedule_resize(event):
        root.after_idle(on_resize)
    root.bind('<Configure>', schedule_resize)

    root.mainloop()

if __name__ == "__main__":
    main()
