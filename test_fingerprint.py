"""
Test acoustic fingerprinting standalone
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.fingerprinter import AcousticFingerprinter
from config import Config


def main():
    print("\n" + "="*60)
    print("🔊 ACOUSTIC FINGERPRINTING TEST")
    print("="*60 + "\n")
    
    audio_dir = Config.AUDIO_SAMPLES_DIR
    
    # Check for audio files
    audio_files = []
    for ext in Config.SUPPORTED_FORMATS:
        audio_files.extend(audio_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}")
        print(f"\n💡 Add audio files (.mp3, .wav, etc.) to test")
        return 1
    
    print(f"✅ Found {len(audio_files)} audio file(s)\n")
    
    # Initialize fingerprinter
    fingerprinter = AcousticFingerprinter()
    
    # Build database
    print("🔨 Building fingerprint database...")
    num_songs = fingerprinter.build_database(audio_dir, force_rebuild=True)
    
    if num_songs == 0:
        print("❌ No songs indexed")
        return 1
    
    # Test with first audio file
    test_audio = audio_files[0]
    print(f"\n{'='*60}")
    print(f"🎵 Testing with: {test_audio.name}")
    print(f"{'='*60}")
    
    results = fingerprinter.match_audio(str(test_audio), top_k=5)
    
    print(fingerprinter.get_match_summary(results))
    
    fingerprinter.close()
    
    print("\n✅ Test complete!")
    print("\n💡 To use in main pipeline:")
    print(f"   python main.py {test_audio} --use-fingerprint")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())