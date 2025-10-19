"""
LyricMatch - Lyrics-based Song Recognition System
"""

from .audio_processor import AudioProcessor
from .transcriber import Transcriber

__version__ = "0.1.0"
__all__ = ["AudioProcessor", "Transcriber"]