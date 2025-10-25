"""
Test script to verify WaveSeek setup
Run this to ensure all components are working
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test if all required libraries are installed"""
    print("\n" + "="*60)
    print("📦 Testing Library Imports")
    print("="*60 + "\n")
    
    libraries = {
        'whisper': 'OpenAI Whisper',
        'librosa': 'Librosa',
        'pydub': 'PyDub',
        'soundfile': 'SoundFile',
        'torch': 'PyTorch',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'fastapi': 'FastAPI',
        'nltk': 'NLTK',
        'sentence_transformers': 'Sentence-Transformers'
    }
    
    failed = []
    for lib, name in libraries.items():
        try:
            __import__(lib)
            print(f"✅ {name:25s} - OK")
        except ImportError:
            print(f"❌ {name:25s} - FAILED")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️  Failed imports: {', '.join(failed)}")
        return False
    else:
        print("\n✅ All libraries imported successfully!")
        return True


def test_config():
    """Test configuration"""
    print("\n" + "="*60)
    print("⚙️  Testing Configuration")
    print("="*60 + "\n")
    
    try:
        from config import Config
        
        print(f"📁 Data directory: {Config.DATA_DIR}")
        print(f"💾 Database path: {Config.DB_PATH}")
        print(f"🎤 Whisper model: {Config.WHISPER_MODEL}")
        print(f"🔍 Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
        print(f"🧠 Matching engine: {Config.MATCHING_ENGINE}")
        print(f"📊 SBERT model: {Config.SBERT_MODEL}")
        
        # Check if directories exist
        if Config.DATA_DIR.exists():
            print(f"\n✅ Directory structure exists")
        else:
            print(f"\n⚠️  Creating directories...")
            Config.create_directories()
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_audio_processor():
    """Test audio processor"""
    print("\n" + "="*60)
    print("🎵 Testing Audio Processor")
    print("="*60 + "\n")
    
    try:
        from src.audio_processor import AudioProcessor
        
        processor = AudioProcessor()
        print(f"✅ AudioProcessor initialized")
        print(f"   Sample rate: {processor.sample_rate} Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processor test failed: {e}")
        return False


def test_transcriber():
    """Test transcriber initialization"""
    print("\n" + "="*60)
    print("🎤 Testing Transcriber (Whisper)")
    print("="*60 + "\n")
    
    try:
        from src.transcriber import Transcriber
        import torch
        
        print(f"🔧 PyTorch device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        print(f"📥 Loading Whisper model (this may take a moment)...\n")
        
        transcriber = Transcriber(model_name="tiny")  # Use tiny for quick test
        print(f"\n✅ Transcriber initialized with model: {transcriber.model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcriber test failed: {e}")
        return False


def check_nltk_data():
    """Download required NLTK data"""
    print("\n" + "="*60)
    print("📚 Checking NLTK Data")
    print("="*60 + "\n")
    
    try:
        import nltk
        
        required_data = ['stopwords', 'punkt', 'punkt_tab']
        
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}' if 'punkt' in data else f'corpora/{data}')
                print(f"✅ {data} - Already downloaded")
            except LookupError:
                print(f"⬇️  Downloading {data}...")
                nltk.download(data, quiet=True)
                print(f"✅ {data} - Downloaded")
        
        return True
        
    except Exception as e:
        print(f"⚠️  NLTK data check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "WAVESEEK SETUP TEST" + " "*22 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Library Imports", test_imports),
        ("Configuration", test_config),
        ("Audio Processor", test_audio_processor),
        ("NLTK Data", check_nltk_data),
        ("Transcriber", test_transcriber),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s} - {status}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! WaveSeek is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Add some test audio files to: data/audio_samples/")
        print("   2. Prepare a lyrics database: python setup_database.py")
        print("   3. Run the complete pipeline: python main.py <audio_file>")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())