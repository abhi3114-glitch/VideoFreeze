"""
Face Detection Module

Detects faces using OpenCV Haar Cascades and scores clarity.
"""

import cv2
import numpy as np
from typing import Tuple


# Load Haar Cascade classifier (pre-trained, comes with OpenCV)
_face_cascade = None


def _get_face_cascade():
    """Lazy load the face cascade classifier."""
    global _face_cascade
    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    return _face_cascade


def detect_faces(frame: np.ndarray) -> Tuple[float, int]:
    """
    Detect faces in a frame and calculate clarity score.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Tuple of (face_score, face_count)
        - face_score: 0-100 score based on face presence and size
        - face_count: Number of faces detected
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Get frame dimensions
    height, width = gray.shape
    frame_area = height * width
    
    # Detect faces
    face_cascade = _get_face_cascade()
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    face_count = len(faces)
    
    # Calculate score based on face presence and size
    if face_count == 0:
        return 0.0, 0
    
    # Calculate total face area
    total_face_area = 0
    for (x, y, w, h) in faces:
        total_face_area += w * h
    
    # Calculate face coverage percentage
    face_coverage = (total_face_area / frame_area) * 100
    
    # Score calculation:
    # - Base score from face coverage (larger faces = better)
    # - Bonus for optimal face count (1-3 faces ideal for thumbnails)
    # - Penalty for too many faces (>5 can be cluttered)
    
    base_score = min(face_coverage * 3, 70)  # Cap at 70 from coverage
    
    if 1 <= face_count <= 3:
        count_bonus = 30  # Ideal face count
    elif face_count == 4:
        count_bonus = 20
    elif face_count == 5:
        count_bonus = 10
    else:
        count_bonus = 5  # Too many faces
    
    total_score = min(base_score + count_bonus, 100)
    
    return float(total_score), face_count


def get_face_regions(frame: np.ndarray) -> list:
    """
    Get bounding boxes of detected faces.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        List of tuples (x, y, w, h) for each face
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = _get_face_cascade()
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
