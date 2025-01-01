"""
Sharpness Analyzer Module

Calculates frame sharpness using Laplacian variance method.
"""

import cv2
import numpy as np


def calculate_sharpness(frame: np.ndarray) -> float:
    """
    Calculate sharpness score using Laplacian variance.
    
    Higher values indicate sharper, more in-focus images.
    
    Args:
        frame: Input frame (BGR or grayscale)
        
    Returns:
        Sharpness score normalized to 0-100 range
    """
    # Convert to grayscale if needed
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    
    # Calculate Laplacian
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # Calculate variance of Laplacian
    variance = laplacian.var()
    
    # Normalize to 0-100 scale
    # Typical variance values range from 0 (blurry) to 1000+ (sharp)
    # We'll use a sigmoid-like normalization
    normalized_score = min(100, (variance / 10.0))
    
    return float(normalized_score)


def is_sharp(frame: np.ndarray, threshold: float = 30.0) -> bool:
    """
    Check if a frame is considered sharp based on threshold.
    
    Args:
        frame: Input frame
        threshold: Minimum sharpness score to be considered sharp
        
    Returns:
        True if frame is sharp, False otherwise
    """
    sharpness = calculate_sharpness(frame)
    return sharpness >= threshold
