# WaveSeek Tests

This directory contains all test scripts for the WaveSeek project.

## Test Files

### `test_setup.py`
Verifies that all required libraries are installed and components can be initialized properly.

**Usage:**
```bash
python tests/test_setup.py
```

**What it tests:**
- Library imports (Whisper, PyTorch, scikit-learn, etc.)
- Configuration loading
- Audio processor initialization
- Transcriber initialization
- NLTK data availability

### `test_transcription.py`
Tests audio transcription on sample files in the `data/audio_samples/` directory.

**Usage:**
```bash
python tests/test_transcription.py
```

**Prerequisites:**
- Audio files in `data/audio_samples/`
- Supported formats: .mp3, .wav, .m4a, .flac, .ogg

**Output:**
- Audio file information (duration, format, sample rate)
- Transcribed text
- Detected language
- Segment timestamps

### `test_compare_matchers.py`
Comprehensive comparison between TF-IDF and Neural Embeddings matching approaches.

**Usage:**
```bash
python tests/test_compare_matchers.py
```

**Prerequisites:**
- Database must be set up (`python setup_database.py`)
- Both matchers initialized

**What it tests:**
- Single query comparison (TF-IDF vs Neural)
- Batch query comparison
- Semantic similarity (paraphrasing test)
- Performance metrics (speed, accuracy)
- Match agreement rates

**Output:**
- Comparison results with timing
- Agreement statistics
- CSV file with batch results: `data/processed/comparison_results.csv`

### `test_apis.py`
Tests external API endpoints (Spotify, YouTube).

**Usage:**
```bash
# First, start the API server
python api.py

# Then in another terminal
python tests/test_apis.py
```

**What it tests:**
- API server health check
- Spotify search endpoint
- YouTube search endpoint
- Connection handling and error messages

## Running All Tests

To run all tests in sequence:

```bash
# Setup and prerequisites
python tests/test_setup.py

# Transcription test (requires audio files)
python tests/test_transcription.py

# Matcher comparison (requires database)
python tests/test_compare_matchers.py

# API tests (requires API server running)
python tests/test_apis.py
```

## Test Requirements

### Minimal Setup
```bash
python tests/test_setup.py
```
Only requires installed packages.

### Audio Processing
```bash
python tests/test_transcription.py
```
Requires:
- Audio files in `data/audio_samples/`

### Matching Tests
```bash
python tests/test_compare_matchers.py
```
Requires:
- Database setup (`python setup_database.py`)
- CSV files in `data/raw/csv/`

### API Tests
```bash
python tests/test_apis.py
```
Requires:
- API server running (`python api.py`)
- API keys configured (if applicable)

## Expected Output

### ✅ All Tests Pass
```
Results: 5/5 tests passed
🎉 All tests passed! WaveSeek is ready to use.
```

### ⚠️ Some Tests Fail
If tests fail, check:
1. **Import errors**: Install missing packages with `pip install -r requirements.txt`
2. **Directory errors**: Run `python setup_database.py` to create directories
3. **Audio errors**: Add audio files to `data/audio_samples/`
4. **Database errors**: Run `python setup_database.py`
5. **API errors**: Start the API server with `python api.py`

## Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### "Database not found"
```bash
python setup_database.py
```

### "No audio files found"
```bash
# Add audio files to:
# data/audio_samples/song1.mp3
# data/audio_samples/song2.wav
```

### "API connection refused"
```bash
# Start the API server
python api.py
```

## Writing New Tests

To add new tests, create a new file in this directory:

```python
"""
Description of what this test does
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Your imports
from config import Config

def test_something():
    """Test description"""
    # Your test code
    pass

if __name__ == "__main__":
    test_something()
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Setup Tests
  run: python tests/test_setup.py

- name: Run Transcription Tests
  run: python tests/test_transcription.py
  if: success()
```