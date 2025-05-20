# model.py
# Contains functions for file operations: listing images, moving images, and creating thumbnails.
# This file encapsulates data and file manipulation logic, following the MVC pattern for separation of concerns.

from pathlib import Path
import os
import shutil
from PIL import Image, ImageTk

def list_images(folder: Path) -> list[Path]:
    """
    Return a sorted list of image file paths in the given folder.
    """
    supported = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    return sorted([folder / f for f in os.listdir(folder)
                   if f.lower().endswith(supported)])

def move_image(src: Path, dest_folder: Path) -> None:
    """
    Move image file to the destination folder.
    Raises exception on failure.
    """
    dest_folder.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest_folder))

def create_thumbnail(image_path: Path, size=(600, 400)) -> ImageTk.PhotoImage:
    """
    Create a thumbnail for the given image path and return a PhotoImage.
    """
    img = Image.open(image_path)
    img.thumbnail(size)
    return ImageTk.PhotoImage(img)
