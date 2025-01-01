"""
VideoFreeze Export Module

Handles frame export and metadata generation.
"""

from .frame_saver import save_frame
from .metadata_generator import generate_metadata

__all__ = ['save_frame', 'generate_metadata']
