"""
Build acoustic fingerprint database from audio files
Run this once to enable fingerprint matching
"""
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from src.fingerprinter import AcousticFingerprinter
from config import Config


def main():
    """Build fingerprint database"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*10 + "ACOUSTIC FINGERPRINT BUILDER" + " "*19 + "║")
    print("╚" + "="*58 + "╝\n")
    
    audio_dir = Config.AUDIO_SAMPLES_DIR
    
    print(f"📂 Audio directory: {audio_dir}")
    
    if not audio_dir.exists():
        print(f"\n❌ Directory not found!")
        print(f"   Create it and add audio files: {audio_dir}")
        return 1
    
    # Check for audio files
    audio_files = []
    for ext in Config.SUPPORTED_FORMATS:
        audio_files.extend(audio_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"\n⚠️  No audio files found in {audio_dir}")
        print(f"\nℹ️  Add audio files (.mp3, .wav, .m4a, etc.) to:")
        print(f"   {audio_dir}")
        return 1
    
    print(f"\n✅ Found {len(audio_files)} audio file(s)")
    
    # Confirm
    response = input("\n🔨 Build fingerprint database? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return 0
    
    # Build
    fingerprinter = AcousticFingerprinter()
    
    try:
        num_songs = fingerprinter.build_database(
            audio_dir=audio_dir,
            force_rebuild=True
        )
        
        if num_songs > 0:
            print(f"\n{'='*60}")
            print(f"✅ Fingerprint database built successfully!")
            print(f"{'='*60}")
            print(f"\n📊 Statistics:")
            print(f"   Songs indexed: {num_songs}")
            print(f"   Unique hashes: {len(fingerprinter.fingerprint_db)}")
            print(f"\n💾 Cache saved to:")
            print(f"   {fingerprinter.cache_path}")
            print(f"\n🎯 Next steps:")
            print(f"   1. Run with fingerprinting: python main.py audio.wav --use-fingerprint")
            print(f"   2. Or use hybrid API with fingerprint_enabled=true")
            
            return 0
        else:
            print("\n❌ No songs were indexed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        fingerprinter.close()


if __name__ == "__main__":
    sys.exit(main())