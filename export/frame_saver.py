"""
Frame Saver Module

Saves frames as PNG or JPG with quality settings.
"""

import cv2
import numpy as np
import os
from datetime import datetime
from pathlib import Path


def save_frame(
    frame: np.ndarray, 
    output_path: str = None,
    format: str = 'png',
    quality: int = 95
) -> str:
    """
    Save a frame to disk as PNG or JPG.
    
    Args:
        frame: Frame to save (BGR format)
        output_path: Path to save to (if None, generates unique filename)
        format: 'png' or 'jpg'
        quality: JPG quality (0-100), ignored for PNG
        
    Returns:
        Path where frame was saved
    """
    # Generate filename if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"thumbnail_{timestamp}.{format.lower()}"
    
    # Ensure parent directory exists
    parent_dir = os.path.dirname(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    # Save based on format
    format_lower = format.lower()
    
    if format_lower == 'png':
        # PNG uses lossless compression
        success = cv2.imwrite(output_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    elif format_lower in ['jpg', 'jpeg']:
        # JPG uses quality parameter
        success = cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'png' or 'jpg'")
    
    if not success:
        raise RuntimeError(f"Failed to save frame to {output_path}")
    
    return output_path


def create_export_directory(base_name: str = "exports") -> str:
    """
    Create an export directory with timestamp.
    
    Args:
        base_name: Base name for export directory
        
    Returns:
        Path to created directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{base_name}_{timestamp}"
    
    os.makedirs(dir_name, exist_ok=True)
    
    return dir_name
