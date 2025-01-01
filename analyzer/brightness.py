"""
Brightness Balance Analyzer Module

Analyzes brightness distribution and exposure balance.
"""

import cv2
import numpy as np


def calculate_brightness_balance(frame: np.ndarray) -> float:
    """
    Calculate brightness balance score using histogram analysis.
    
    Checks for proper exposure by analyzing the distribution of pixel intensities.
    Penalizes overexposed (clipped whites) and underexposed (crushed blacks).
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Brightness balance score (0-100)
    """
    # Convert to grayscale for brightness analysis
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist.flatten()
    
    # Normalize histogram
    total_pixels = gray.shape[0] * gray.shape[1]
    hist_norm = hist / total_pixels
    
    # Calculate statistics
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    
    # Check for clipping (overexposure and underexposure)
    # Count pixels in extreme ranges
    dark_pixels = np.sum(hist_norm[0:10])  # Very dark pixels
    bright_pixels = np.sum(hist_norm[246:256])  # Very bright pixels
    
    # Ideal brightness is around 100-150 (middle range)
    # Calculate how close to ideal the mean is
    ideal_brightness = 127
    brightness_deviation = abs(mean_brightness - ideal_brightness) / 127
    brightness_score = (1 - brightness_deviation) * 50
    
    # Penalize clipping
    clipping_penalty = (dark_pixels + bright_pixels) * 100
    clipping_score = max(0, 30 - clipping_penalty)
    
    # Reward good contrast (standard deviation in reasonable range)
    # Ideal std is around 40-80
    if 40 <= std_brightness <= 80:
        contrast_score = 20
    elif 30 <= std_brightness < 40 or 80 < std_brightness <= 100:
        contrast_score = 15
    elif 20 <= std_brightness < 30 or 100 < std_brightness <= 120:
        contrast_score = 10
    else:
        contrast_score = 5
    
    # Combine scores
    total_score = brightness_score + clipping_score + contrast_score
    
    return float(min(100, max(0, total_score)))


def get_brightness_stats(frame: np.ndarray) -> dict:
    """
    Get detailed brightness statistics for a frame.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Dictionary with brightness statistics
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    total_pixels = gray.shape[0] * gray.shape[1]
    hist_norm = hist.flatten() / total_pixels
    
    return {
        'mean': float(np.mean(gray)),
        'std': float(np.std(gray)),
        'min': float(np.min(gray)),
        'max': float(np.max(gray)),
        'dark_pixels_pct': float(np.sum(hist_norm[0:10]) * 100),
        'bright_pixels_pct': float(np.sum(hist_norm[246:256]) * 100)
    }
