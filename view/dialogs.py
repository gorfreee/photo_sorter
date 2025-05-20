# dialogs.py
# Contains dialog functions for showing info, warning, error messages, and category configuration dialogs.
# This file keeps UI dialog logic modular and reusable within the view layer.

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog


def show_info(message: str) -> None:
    messagebox.showinfo("Info", message)


def show_warning(message: str) -> None:
    messagebox.showwarning("Warning", message)


def show_error(message: str) -> None:
    messagebox.showerror("Error", message)


def configure_category(root: tk.Tk, idx: int, initial: dict) -> dict:
    """
    Show a dialog to configure category name and path.
    Returns a dict with action: 'save', 'delete', or 'cancel', and data for saving.
    """
    result = {'action': 'cancel'}

    dialog = tk.Toplevel(root)
    dialog.title(f"Edit Category {idx+1}")
    dialog.grab_set()

    tk.Label(dialog, text=f"Category {idx+1} Name:").pack(padx=10, pady=5)
    name_var = tk.StringVar(value=initial.get('name', ''))
    path_var = tk.StringVar(value=initial.get('path', ''))

    tk.Entry(dialog, textvariable=name_var, width=20).pack(padx=10, pady=2)
    tk.Label(dialog, text="Destination Folder:").pack(padx=10, pady=5)
    path_frame = tk.Frame(dialog)
    path_frame.pack(padx=10, pady=2)
    tk.Entry(path_frame, textvariable=path_var, width=30).pack(side=tk.LEFT)
    tk.Button(path_frame, text="Browse", command=lambda: path_var.set(filedialog.askdirectory())).pack(side=tk.LEFT, padx=5)

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)

    def on_save():
        name = name_var.get().strip()
        path = path_var.get().strip()
        if not name or not path:
            show_warning("Please enter both a name and a folder.")
            return
        result['action'] = 'save'
        result['name'] = name
        result['path'] = path
        dialog.destroy()

    def on_delete():
        result['action'] = 'delete'
        dialog.destroy()

    def on_cancel():
        result['action'] = 'cancel'
        dialog.destroy()

    tk.Button(btn_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete", command=on_delete).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

    root.wait_window(dialog)
    return result
