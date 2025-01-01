"""
Aesthetic Scorer Module

Combines all individual metrics to produce an overall aesthetic score.
"""

import numpy as np
from typing import Dict, Tuple, List
from .sharpness import calculate_sharpness
from .face_detector import detect_faces
from .brightness import calculate_brightness_balance
from .composition import calculate_composition_score


# Default weights for combining scores
DEFAULT_WEIGHTS = {
    'sharpness': 0.30,
    'face_clarity': 0.25,
    'brightness': 0.20,
    'composition': 0.25
}


def score_frame(frame: np.ndarray, weights: Dict[str, float] = None) -> Dict[str, float]:
    """
    Calculate comprehensive aesthetic score for a frame.
    
    Args:
        frame: Input frame (BGR)
        weights: Optional custom weights for each metric
        
    Returns:
        Dictionary containing individual scores and overall score
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Calculate individual scores
    sharpness = calculate_sharpness(frame)
    face_score, face_count = detect_faces(frame)
    brightness = calculate_brightness_balance(frame)
    composition = calculate_composition_score(frame)
    
    # Calculate weighted overall score
    overall_score = (
        sharpness * weights['sharpness'] +
        face_score * weights['face_clarity'] +
        brightness * weights['brightness'] +
        composition * weights['composition']
    )
    
    return {
        'overall': float(overall_score),
        'sharpness': float(sharpness),
        'face_clarity': float(face_score),
        'face_count': int(face_count),
        'brightness': float(brightness),
        'composition': float(composition)
    }


def find_best_frame(
    frames: List[Tuple[np.ndarray, float]], 
    weights: Dict[str, float] = None,
    progress_callback = None
) -> Tuple[int, np.ndarray, float, Dict[str, float]]:
    """
    Find the frame with the highest aesthetic score.
    
    Args:
        frames: List of tuples (frame, timestamp)
        weights: Optional custom weights for scoring
        progress_callback: Optional callback function(current, total) for progress
        
    Returns:
        Tuple of (best_index, best_frame, best_timestamp, best_scores)
    """
    if not frames:
        raise ValueError("No frames provided")
    
    best_index = 0
    best_score = -1
    best_scores_dict = None
    
    for i, (frame, timestamp) in enumerate(frames):
        scores = score_frame(frame, weights)
        
        if scores['overall'] > best_score:
            best_score = scores['overall']
            best_index = i
            best_scores_dict = scores
        
        # Call progress callback if provided
        if progress_callback:
            progress_callback(i + 1, len(frames))
    
    best_frame, best_timestamp = frames[best_index]
    
    return best_index, best_frame, best_timestamp, best_scores_dict


def score_all_frames(
    frames: List[Tuple[np.ndarray, float]], 
    weights: Dict[str, float] = None,
    progress_callback = None
) -> List[Tuple[float, Dict[str, float]]]:
    """
    Score all frames and return results.
    
    Args:
        frames: List of tuples (frame, timestamp)
        weights: Optional custom weights for scoring
        progress_callback: Optional callback function(current, total) for progress
        
    Returns:
        List of tuples (timestamp, scores_dict) for each frame
    """
    results = []
    
    for i, (frame, timestamp) in enumerate(frames):
        scores = score_frame(frame, weights)
        results.append((timestamp, scores))
        
        if progress_callback:
            progress_callback(i + 1, len(frames))
    
    return results
