"""
Test transcription on sample audio files
"""
from pathlib import Path
from src.transcriber import Transcriber
from src.audio_processor import AudioProcessor
from config import Config


def test_transcription():
    """Test transcription on available audio files"""
    print("\n" + "="*60)
    print("🎤 Testing Audio Transcription")
    print("="*60 + "\n")
    
    # Check for audio files
    audio_dir = Config.AUDIO_SAMPLES_DIR
    
    audio_files = []
    for ext in Config.SUPPORTED_FORMATS:
        audio_files.extend(audio_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"⚠️  No audio files found in: {audio_dir}")
        print("\n📝 To test transcription:")
        print(f"   1. Place audio files in: {audio_dir}")
        print("   2. Supported formats: " + ", ".join(Config.SUPPORTED_FORMATS))
        print("   3. Run this script again")
        return
    
    print(f"📂 Found {len(audio_files)} audio file(s):\n")
    
    # Initialize components
    audio_processor = AudioProcessor()
    transcriber = Transcriber(model_name="base")
    
    # Process each file
    for i, audio_file in enumerate(audio_files, 1):
        print("="*60)
        print(f"[{i}/{len(audio_files)}] {audio_file.name}")
        print("="*60)
        
        try:
            # Get audio info
            info = audio_processor.get_audio_info(audio_file)
            print(f"\n📊 Audio Info:")
            print(f"   Duration: {info['duration']:.2f}s")
            print(f"   Sample Rate: {info['sample_rate']}Hz")
            print(f"   Format: {info['format']}")
            
            # Transcribe
            result = transcriber.transcribe(audio_file)
            
            print(f"\n📝 Transcription:")
            print(f"   Language: {result['language']}")
            print(f"   Text: \"{result['text']}\"")
            
            if result['segments']:
                print(f"\n⏱️  Segments ({len(result['segments'])}):")
                for seg in result['segments'][:3]:  # Show first 3
                    print(f"   [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
                if len(result['segments']) > 3:
                    print(f"   ... and {len(result['segments']) - 3} more segments")
            
            print()
            
        except Exception as e:
            print(f"\n❌ Error processing {audio_file.name}: {e}\n")
    
    print("="*60)
    print("✅ Transcription test complete!")
    print("="*60)


if __name__ == "__main__":
    test_transcription()