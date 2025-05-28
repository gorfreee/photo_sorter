# model.py
# Contains functions for file operations: listing images, moving images, and creating thumbnails.
# This file encapsulates data and file manipulation logic, following the MVC pattern for separation of concerns.

from pathlib import Path
import os
import shutil
from PIL import Image  # Only import Image, not ImageTk

def list_images(folder: Path) -> list[Path]:
    """
    Return a sorted list of image file paths in the given folder.
    """
    supported = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff', '.webp')
    return sorted([folder / f for f in os.listdir(folder)
                   if f.lower().endswith(supported)])

def move_image(src: Path, dest_folder: Path) -> None:
    """
    Move image file to the destination folder.
    Raises exception on failure.
    """
    dest_folder.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest_folder))

def create_thumbnail(image_path: Path, size=(400, 300)) -> Image.Image:
    """
    Create a thumbnail for the given image path and return a PIL Image object.
    Always resize to the fixed size for consistent Dear PyGui display.
    """
    img = Image.open(image_path)
    img = img.convert("RGBA")
    img = img.resize(size, Image.Resampling.LANCZOS)
    return img  # Return the PIL Image object
