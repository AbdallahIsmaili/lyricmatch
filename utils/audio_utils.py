"""
Audio utility functions for WaveSeek
Handles downloading, renaming, and organizing audio files
"""
import sys
from pathlib import Path

# Add parent directory to path to import from root
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import os
import glob
import yt_dlp
from config import Config


class AudioManager:
    """Manage audio files for testing and processing"""
    
    def __init__(self, audio_dir=None):
        self.audio_dir = audio_dir or Config.AUDIO_SAMPLES_DIR
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def download_youtube_audio(self, urls, output_dir=None):
        """
        Download audio from YouTube URLs
        
        Args:
            urls: List of YouTube URLs
            output_dir: Output directory (default: audio_samples)
        
        Returns:
            Number of successful downloads
        """
        if output_dir is None:
            output_dir = self.audio_dir
        
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "restrictfilenames": True,
            "noplaylist": True,
            "continue_dl": True,
            "ignoreerrors": True,
            "no_warnings": False,
            "quiet": False,
        }
        
        print(f"Starting download of {len(urls)} songs...")
        successful_downloads = 0
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls, 1):
                try:
                    print(f"Downloading {i}/{len(urls)}: {url}")
                    ydl.download([url])
                    successful_downloads += 1
                except Exception as e:
                    print(f"Error downloading {url}: {str(e)}")
                    continue
        
        print(f"Download completed! {successful_downloads}/{len(urls)} songs downloaded successfully.")
        return successful_downloads
    
    def rename_audio_files(self, advanced=False, dry_run=False):
        """
        Rename audio files for better organization
        
        Args:
            advanced: Apply advanced cleaning rules
            dry_run: Show what would be renamed without actually renaming
        
        Returns:
            Number of files renamed
        """
        audio_files = list(self.audio_dir.glob("*.*"))
        
        if not audio_files:
            print(f"No files found in '{self.audio_dir}'")
            return 0
        
        print(f"Found {len(audio_files)} files in '{self.audio_dir}'")
        renamed_count = 0
        
        for old_path in audio_files:
            old_filename = old_path.name
            new_filename = old_filename
            
            # Basic cleaning: spaces to underscores
            new_filename = new_filename.replace(" ", "_")
            
            if advanced:
                # Advanced cleaning rules
                chars_to_remove = '()[]\'"{}'
                for char in chars_to_remove:
                    new_filename = new_filename.replace(char, "")
                
                # Remove common YouTube suffixes
                suffixes = ['_Official', '_Video', '_Audio', '_Lyrics', '_YT']
                for suffix in suffixes:
                    if new_filename.endswith(suffix):
                        new_filename = new_filename[:-len(suffix)]
            
            # Only proceed if filename changed
            if old_filename != new_filename:
                new_path = self.audio_dir / new_filename
                
                if dry_run:
                    print(f"Would rename: '{old_filename}' -> '{new_filename}'")
                    renamed_count += 1
                else:
                    # Check if target already exists
                    if new_path.exists():
                        print(f"Warning: '{new_filename}' already exists. Skipping '{old_filename}'")
                        continue
                    
                    try:
                        old_path.rename(new_path)
                        print(f"Renamed: '{old_filename}' -> '{new_filename}'")
                        renamed_count += 1
                    except Exception as e:
                        print(f"Error renaming '{old_filename}': {str(e)}")
            elif dry_run:
                print(f"No change needed: '{old_filename}'")
        
        return renamed_count
    
    def get_audio_files(self):
        """Get list of all audio files in directory"""
        audio_files = []
        for ext in Config.SUPPORTED_FORMATS:
            audio_files.extend(self.audio_dir.glob(f"*{ext}"))
        return audio_files
    
    def cleanup_audio_files(self, keep_count=10):
        """
        Clean up audio files, keeping only specified number
        
        Args:
            keep_count: Number of files to keep (oldest will be deleted)
        """
        audio_files = self.get_audio_files()
        
        if len(audio_files) <= keep_count:
            print(f"Only {len(audio_files)} files found, no cleanup needed.")
            return
        
        # Sort by modification time (oldest first)
        audio_files.sort(key=lambda x: x.stat().st_mtime)
        
        files_to_delete = audio_files[:-keep_count]
        
        print(f"Cleaning up {len(files_to_delete)} audio files...")
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                print(f"Deleted: {file_path.name}")
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")


# Predefined URLs for common artists
SAMPLE_URLS = [
    # Cardi B
    "https://www.youtube.com/watch?v=PEGccV-NOm8",
    "https://youtu.be/hXnMSaK6C2w",
    "https://youtu.be/8zSRkr1nQNw",
    
    # Charlie Puth
    "https://www.youtube.com/watch?v=nfs8NYg7yQM",
    "https://www.youtube.com/watch?v=3AtDnEC4zak",
    "https://www.youtube.com/watch?v=CwfoyVa980U",
    
    # Add more URLs as needed...
]


def download_sample_audio():
    """Download sample audio files for testing"""
    manager = AudioManager()
    return manager.download_youtube_audio(SAMPLE_URLS)


def rename_audio_cli():
    """CLI interface for renaming audio files"""
    manager = AudioManager()
    
    print("Choose renaming option:")
    print("1. Basic rename (spaces to underscores)")
    print("2. Advanced rename (spaces + remove special characters)")
    print("3. Dry run (show what would be renamed)")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        count = manager.rename_audio_files(advanced=False)
        print(f"\nBasic renaming completed! {count} files were renamed.")
    elif choice == "2":
        count = manager.rename_audio_files(advanced=True)
        print(f"\nAdvanced renaming completed! {count} files were renamed.")
    elif choice == "3":
        count = manager.rename_audio_files(dry_run=True)
        print(f"\nDry run completed. {count} files would be renamed.")
    else:
        print("Invalid choice. Running basic rename...")
        count = manager.rename_audio_files(advanced=False)
        print(f"\nBasic renaming completed! {count} files were renamed.")


if __name__ == "__main__":
    rename_audio_cli()