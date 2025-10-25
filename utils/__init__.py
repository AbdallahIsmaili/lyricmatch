"""
Utility modules for WaveSeek
"""
from .audio_utils import AudioManager, download_sample_audio, rename_audio_cli
from .setup_database import main as setup_database

__all__ = ['AudioManager', 'download_sample_audio', 'rename_audio_cli', 'setup_database']