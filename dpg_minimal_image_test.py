# test: his script demonstrates how to load an image and display it in a Dear PyGui window.


import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image

WIDTH, HEIGHT = 400, 300
TAG = "tex"

def create_red():
    arr = np.ones((HEIGHT, WIDTH, 4), dtype=np.float32)
    arr[:,:,1:] = 0
    arr[:,:,3] = 1  # Set A to 1 (fully opaque)
    return arr.ravel().tolist()

def create_image_texture(image_path):
    pil_image = Image.open(image_path)
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    pil_image = pil_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    img_array = np.asarray(pil_image).astype(np.float32) / 255.0
    return img_array.ravel().tolist()

def set_texture(data):
    dpg.set_value(TAG, data)

def select_and_show_image():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*"))
    )
    root.destroy()
    if file_path:
        try:
            img_data = create_image_texture(file_path)
            set_texture(img_data)
        except Exception as e:
            print(f"Error: {e}")
            set_texture(create_red())
    else:
        set_texture(create_red())

dpg.create_context()
with dpg.texture_registry():
    dpg.add_dynamic_texture(WIDTH, HEIGHT, create_red(), tag=TAG)
with dpg.window(label="Test"):
    dpg.add_button(label="Select Image", callback=select_and_show_image)
    dpg.add_image(TAG, width=WIDTH, height=HEIGHT)
dpg.create_viewport(title="Test", width=500, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
