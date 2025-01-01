"""
Frame Extractor Module

Extracts frames from video files at a configurable sampling rate.
"""

import cv2
import numpy as np
from typing import List, Tuple


def extract_frames(video_path: str, fps: float = 1.0) -> List[Tuple[np.ndarray, float]]:
    """
    Extract frames from a video file at specified FPS.
    
    Args:
        video_path: Path to the video file
        fps: Frames per second to extract (default: 1.0)
        
    Returns:
        List of tuples containing (frame, timestamp_in_seconds)
        
    Raises:
        ValueError: If video cannot be opened
        RuntimeError: If frame extraction fails
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0
    
    if video_fps == 0:
        cap.release()
        raise RuntimeError("Could not determine video FPS")
    
    # Calculate frame interval
    frame_interval = int(video_fps / fps)
    if frame_interval < 1:
        frame_interval = 1
    
    frames = []
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Sample frames at specified interval
            if frame_count % frame_interval == 0:
                timestamp = frame_count / video_fps
                frames.append((frame.copy(), timestamp))
            
            frame_count += 1
            
    finally:
        cap.release()
    
    if len(frames) == 0:
        raise RuntimeError("No frames were extracted from video")
    
    return frames


def get_video_info(video_path: str) -> dict:
    """
    Get metadata about a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary containing video metadata
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        'fps': fps,
        'total_frames': total_frames,
        'width': width,
        'height': height,
        'duration': duration,
        'resolution': f"{width}x{height}"
    }
