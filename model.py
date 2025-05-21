"""
model.py
Contains functions for file operations: listing images, moving images, and creating thumbnails.
This file encapsulates data and file manipulation logic, following the MVC pattern for separation of concerns.
"""

import os
import shutil
import numpy as np
from pathlib import Path
from PIL import Image

def list_images(folder: Path) -> list[Path]:
    """
    Return a sorted list of image file paths in the given folder.
    """
    if not folder or not folder.exists():
        return []
        
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

def create_thumbnail(image_path: Path, max_size=(800, 600)) -> np.ndarray:
    """
    Create a thumbnail for the given image path and return a numpy array
    suitable for DearPyGui texture.
    """
    img = Image.open(image_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calculate thumbnail size while maintaining aspect ratio
    width, height = img.size
    scale = min(max_size[0] / width, max_size[1] / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize the image
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return np.array(img)
