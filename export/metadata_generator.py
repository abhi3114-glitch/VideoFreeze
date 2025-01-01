"""
Metadata Generator Module

Generates metadata summaries for exported frames.
"""

from datetime import datetime
from typing import Dict
import json


def generate_metadata(
    video_path: str,
    video_info: Dict,
    frame_timestamp: float,
    scores: Dict[str, float],
    total_frames_analyzed: int,
    processing_time: float,
    output_path: str = None
) -> str:
    """
    Generate metadata summary file for an exported frame.
    
    Args:
        video_path: Path to source video
        video_info: Video metadata dictionary
        frame_timestamp: Timestamp of selected frame
        scores: Aesthetic scores dictionary
        total_frames_analyzed: Number of frames analyzed
        processing_time: Time taken to process (seconds)
        output_path: Path to save metadata (if None, generates filename)
        
    Returns:
        Path where metadata was saved
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"thumbnail_metadata_{timestamp}.txt"
    
    # Format timestamp as MM:SS
    minutes = int(frame_timestamp // 60)
    seconds = int(frame_timestamp % 60)
    time_formatted = f"{minutes:02d}:{seconds:02d}"
    
    # Create metadata content
    metadata_lines = [
        "=" * 60,
        "VideoFreeze - Thumbnail Frame Metadata",
        "=" * 60,
        "",
        "VIDEO INFORMATION",
        "-" * 60,
        f"Source File: {video_path}",
        f"Resolution: {video_info.get('resolution', 'N/A')}",
        f"Duration: {video_info.get('duration', 0):.2f} seconds",
        f"FPS: {video_info.get('fps', 0):.2f}",
        f"Total Frames: {video_info.get('total_frames', 0)}",
        "",
        "SELECTED FRAME",
        "-" * 60,
        f"Timestamp: {time_formatted} ({frame_timestamp:.2f} seconds)",
        f"Frame Position: {int(frame_timestamp * video_info.get('fps', 0))}",
        "",
        "AESTHETIC SCORES",
        "-" * 60,
        f"Overall Score: {scores.get('overall', 0):.2f}/100",
        "",
        "Individual Metrics:",
        f"  • Sharpness:     {scores.get('sharpness', 0):.2f}/100",
        f"  • Face Clarity:  {scores.get('face_clarity', 0):.2f}/100",
        f"  • Brightness:    {scores.get('brightness', 0):.2f}/100",
        f"  • Composition:   {scores.get('composition', 0):.2f}/100",
        "",
        f"Faces Detected: {scores.get('face_count', 0)}",
        "",
        "PROCESSING STATISTICS",
        "-" * 60,
        f"Frames Analyzed: {total_frames_analyzed}",
        f"Processing Time: {processing_time:.2f} seconds",
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "=" * 60,
    ]
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(metadata_lines))
    
    return output_path


def generate_metadata_json(
    video_path: str,
    video_info: Dict,
    frame_timestamp: float,
    scores: Dict[str, float],
    total_frames_analyzed: int,
    processing_time: float,
    output_path: str = None
) -> str:
    """
    Generate metadata in JSON format.
    
    Args:
        Same as generate_metadata
        
    Returns:
        Path where JSON metadata was saved
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"thumbnail_metadata_{timestamp}.json"
    
    metadata = {
        'video': {
            'source_file': video_path,
            'resolution': video_info.get('resolution', 'N/A'),
            'duration_seconds': video_info.get('duration', 0),
            'fps': video_info.get('fps', 0),
            'total_frames': video_info.get('total_frames', 0)
        },
        'selected_frame': {
            'timestamp_seconds': frame_timestamp,
            'frame_number': int(frame_timestamp * video_info.get('fps', 0))
        },
        'aesthetic_scores': scores,
        'processing': {
            'frames_analyzed': total_frames_analyzed,
            'processing_time_seconds': processing_time,
            'analysis_date': datetime.now().isoformat()
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return output_path
