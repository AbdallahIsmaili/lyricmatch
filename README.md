# 🎵 WaveSeek AI - Multilingual Song Recognition System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-000000.svg)](https://flask.palletsprojects.com/)

> **Advanced AI-powered audio recognition pipeline starting with multilingual song identification through sophisticated lyric matching. The foundation for our ambitious roadmap toward universal sound recognition.**

---

## 🌟 Overview

WaveSeek AI is a comprehensive audio recognition system that identifies songs through intelligent lyric transcription and matching. Unlike traditional audio fingerprinting systems (like Shazam), we analyze the semantic content of lyrics using state-of-the-art AI models, making our system uniquely capable of:

- **Multilingual Recognition**: Automatic language detection across 90+ languages
- **Semantic Understanding**: Neural embeddings (BERT) for contextual meaning analysis
- **Robust Matching**: Handles variations, paraphrases, and noisy audio
- **Tiered Architecture**: Scalable from free basic matching to premium AI models

### 🎯 Current Capabilities

- ✅ **Speech-to-Text Transcription** via OpenAI Whisper (5 model sizes)
- ✅ **Multiple Matching Engines**: TF-IDF, Neural Embeddings (SBERT), Hybrid
- ✅ **Real-time Processing** with progress tracking
- ✅ **Modern Web Interface** built with React + Flask
- ✅ **Database Management** with SQLite and CSV import
- ✅ **Streaming Integration** (Spotify, YouTube)

### 🚀 Vision & Roadmap

This project is **Phase 1** of our ambitious audio AI pipeline:

**🎵 Phase 1 (Current)**: Song Recognition via Lyrics
- Multilingual lyric matching
- Neural semantic understanding
- Production-ready web application

**🎙️ Phase 2 (In Development)**: Voice Biometrics
- Speaker gender classification
- Age estimation from voice
- Emotion and sentiment detection
- Voice characteristic profiling

**🔊 Phase 3 (Future)**: Universal Sound Database
- Human voice recognition (accents, dialects)
- Animal sound identification
- Mechanical sound classification
- Environmental audio analysis
- Real-time multi-source audio scene understanding

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Matching Engines](#-matching-engines)
- [Configuration](#-configuration)
- [Development](#-development)
- [Performance](#-performance)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| 🎤 **Whisper Transcription** | OpenAI Whisper models (tiny → large) for accurate speech-to-text |
| 🧠 **Neural Embeddings** | Sentence-BERT for semantic understanding beyond keywords |
| 🌍 **90+ Languages** | Automatic language detection and multilingual support |
| ⚡ **Multiple Engines** | TF-IDF (fast), Neural (accurate), Hybrid (best of both) |
| 📊 **Real-time Progress** | Live status updates with visual waveform display |
| 🎨 **Modern UI** | Responsive React interface with dark/light themes |
| 📈 **History Tracking** | IndexedDB-based search history with replay |
| 🎵 **Streaming Links** | Direct Spotify & YouTube integration |

### Advanced Features

- **Tiered System**: Free and Premium plans with different model access
- **Batch Processing**: Process multiple audio files simultaneously
- **Confidence Scoring**: Detailed match explanations with confidence metrics
- **Caching System**: Smart embeddings cache for instant subsequent searches
- **Database Management**: SQLite with CSV import/export capabilities
- **Audio Analysis**: Sample rate, duration, and quality metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │Processing│  │ Results  │  │ History  │   │
│  │   View   │→ │   View   │→ │   View   │  │  Modal   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask API)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Upload    │→ │  Processing  │→ │   Results    │     │
│  │   Endpoint   │  │    Thread    │  │   Endpoint   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Processing Pipeline                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Audio   │→ │ Whisper  │→ │   Text   │→ │ Matching │   │
│  │Processor │  │Transcribe│  │Processor │  │  Engine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer                                 │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   SQLite DB  │         │  Embeddings  │                 │
│  │ (Lyrics Data)│         │    Cache     │                 │
│  └──────────────┘         └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**
- **Flask** - Lightweight web framework
- **OpenAI Whisper** - State-of-the-art speech recognition
- **Sentence-BERT** - Neural text embeddings
- **Librosa** - Audio processing and analysis
- **scikit-learn** - TF-IDF vectorization
- **SQLite** - Lyrics database management

**Frontend**
- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Beautiful iconography
- **IndexedDB** - Client-side history storage

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- 4GB+ RAM (8GB+ recommended for large models)
- Optional: CUDA-capable GPU for faster processing

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/AbdallahIsmaili/waveseek.git
cd waveseek

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Frontend Setup

```bash
# Navigate to frontend directory (if separate)
cd frontend  # or wherever your React app is located

# Install dependencies
npm install

# Build for production
npm run build
```

### Database Setup

```bash
# Create directory structure
python -c "from config import Config; Config.create_directories()"

# Place your lyrics CSV files in data/raw/csv/

# Initialize database using the utils version
python -m utils.setup_database

# Download audio samples
python -m utils.audio_utils download_sample_audio

# Rename audio files (interactive)
python -m utils.audio_utils rename_audio_cli

# Or use programmatically
from utils.audio_utils import AudioManager
manager = AudioManager()
manager.download_youtube_audio(["https://youtube.com/..."])
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Spotify API (optional, for streaming links)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# YouTube API (optional, for streaming links)
YOUTUBE_API_KEY=your_youtube_api_key

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
```

---

## 🚀 Quick Start

### Running the Application

**Development Mode:**

```bash
# Terminal 1 - Start Flask backend
python api/api.py

# Terminal 2 - Start React frontend (if separate)
cd frontend
npm start
```

**Production Mode:**

```bash
# Run Flask with production server
gunicorn -w 4 -b 0.0.0.0:5000 api.api:app
```

The application will be available at `http://localhost:5000`

### First Upload

1. Open your browser to `http://localhost:5000`
2. Select your tier (Free or Premium)
3. Configure settings:
   - **Whisper Model**: Choose based on speed vs accuracy tradeoff
   - **Matching Engine**: TF-IDF (fast), Neural (accurate), or Hybrid
4. Upload an audio file (MP3, WAV, M4A, FLAC, or OGG)
5. Watch real-time processing with waveform visualization
6. Get results with confidence scores and streaming links

---

## 📖 Usage

### Command Line Interface

For batch processing or integration:

```bash
# Basic usage with default settings
python main.py audio/mysong.wav

# Specify Whisper model and matching engine
python main.py audio/mysong.wav -m base -e neural

# Force specific language (skip auto-detection)
python main.py audio/mysong.wav -l ko  # Korean

# Get top 10 matches
python main.py audio/mysong.wav -k 10

# Batch process directory
python main.py audio_folder/ -b -o results.csv

# Use specific SBERT model
python main.py audio/mysong.wav -e neural -s all-mpnet-base-v2

# Rebuild embeddings cache
python main.py audio/mysong.wav --rebuild-embeddings
```

### Python API

```python
from main import WaveSeek

# Initialize with custom configuration
waveseek = WaveSeek(
    whisper_model='base',      # tiny, base, small, medium, large
    language='en',              # or None for auto-detect
    matching_engine='neural'    # tfidf, neural, or hybrid
)

# Identify a song
results = waveseek.identify_song(
    'audio/song.wav',
    preprocess=True,     # Apply noise reduction
    top_k=5,             # Number of matches
    language=None        # Auto-detect language
)

# Access results
if results:
    top_match = results[0]
    print(f"Song: {top_match['title']}")
    print(f"Artist: {top_match['artist']}")
    print(f"Confidence: {top_match['final_score']:.2%}")
    print(f"Language: {top_match['transcription_language']}")

# Clean up
waveseek.close()
```

### Web API

```bash
# Upload and process audio
curl -X POST http://localhost:5000/api/upload \
  -F "audio=@song.wav" \
  -F "tier=premium" \
  -F "whisper_model=base" \
  -F "engine=neural"

# Check processing status
curl http://localhost:5000/api/status/{job_id}

# Search by text query
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "feeling good today", "tier": "free"}'

# Get database statistics
curl http://localhost:5000/api/stats
```

---

## 🔧 API Documentation

### Endpoints

#### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database_songs": 15420
}
```

#### `GET /api/tiers`
Get available tiers and features

**Response:**
```json
{
  "tiers": {
    "free": {
      "name": "Free",
      "whisper_models": ["tiny", "base"],
      "matching_engines": ["tfidf"],
      "max_file_size": 20971520,
      "daily_limit": 5
    },
    "premium": { ... }
  }
}
```

#### `POST /api/upload`
Upload audio file for processing

**Parameters:**
- `audio` (file): Audio file
- `tier` (string): "free" or "premium"
- `whisper_model` (string): Model size
- `engine` (string): Matching engine
- `sbert_model` (string, optional): SBERT model for neural/hybrid

**Response:**
```json
{
  "job_id": "uuid-string",
  "message": "Processing started",
  "tier": "premium"
}
```

#### `GET /api/status/{job_id}`
Get processing status

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "complete",
  "progress": 100,
  "results": [...],
  "transcription": "...",
  "language": "en",
  "audio_info": {...}
}
```

#### `POST /api/search`
Text-based lyric search

**Request:**
```json
{
  "query": "feeling good today",
  "tier": "free"
}
```

**Response:**
```json
{
  "results": [...],
  "query": "feeling good today",
  "tier": "free"
}
```

---

## 🎯 Matching Engines

### TF-IDF (Traditional)

**Best for:** Speed, exact keyword matching

```python
matcher = LyricsMatcher()
results = matcher.match("your query here", top_k=5)
```

**Characteristics:**
- ⚡ **Speed**: 35ms average
- 📊 **Accuracy**: 67% on test dataset
- 💾 **Memory**: ~200MB
- ✅ **Use Case**: Fast lookups, exact phrases

### Neural Embeddings (SBERT)

**Best for:** Semantic understanding, paraphrases

```python
matcher = NeuralLyricsMatcher(model_name='all-MiniLM-L6-v2')
results = matcher.match("your query here", top_k=5)
```

**Characteristics:**
- ⚡ **Speed**: 145ms average (cached)
- 📊 **Accuracy**: 84% on test dataset
- 💾 **Memory**: ~450MB
- ✅ **Use Case**: Semantic similarity, synonyms

**Available Models:**

| Model | Dimensions | Speed | Quality | Best For |
|-------|-----------|-------|---------|----------|
| `all-MiniLM-L6-v2` ⭐ | 384 | ⚡⚡⚡ | ⭐⭐⭐ | General use (recommended) |
| `all-mpnet-base-v2` 🏆 | 768 | ⚡⚡ | ⭐⭐⭐⭐ | Highest quality |
| `paraphrase-MiniLM-L6-v2` | 384 | ⚡⚡⚡ | ⭐⭐⭐ | Paraphrase detection |

### Hybrid (Neural + Fuzzy)

**Best for:** Maximum accuracy

```python
matcher = NeuralLyricsMatcher()
results = matcher.match("your query here", use_fuzzy=True, hybrid_weight=0.7)
```

**Characteristics:**
- ⚡ **Speed**: 168ms average
- 📊 **Accuracy**: 87% on test dataset
- 💾 **Memory**: ~450MB
- ✅ **Use Case**: Best overall results

---

## ⚙️ Configuration

### Whisper Models

| Model | Speed | Accuracy | RAM | Use Case |
|-------|-------|----------|-----|----------|
| `tiny` | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Testing, demos |
| `base` | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | General use |
| `small` | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | Better accuracy |
| `medium` | ⚡⚡ | ⭐⭐⭐⭐ | ~5GB | High accuracy |
| `large` | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | Best accuracy |

### Configuration File

Edit `config.py` to customize:

```python
from config import Config

# Change matching engine
Config.set_matching_engine('neural')  # tfidf, neural, hybrid

# Change SBERT model
Config.set_sbert_model('all-mpnet-base-v2')

# Adjust similarity threshold
Config.SIMILARITY_THRESHOLD = 0.25  # 0-1 scale

# Set hybrid weights
Config.HYBRID_NEURAL_WEIGHT = 0.7  # 70% neural, 30% fuzzy

# Enable/disable embeddings cache
Config.USE_EMBEDDINGS_CACHE = True

# Whisper language
Config.WHISPER_LANGUAGE = None  # None for auto-detect, or 'en', 'ko', etc.
```

### Tier Configuration

Modify `TIER_CONFIGS` in `api/api.py`:

```python
TIER_CONFIGS = {
    'free': {
        'whisper_models': ['tiny', 'base'],
        'matching_engines': ['tfidf'],
        'max_file_size': 20 * 1024 * 1024,  # 20MB
        'daily_limit': 5
    },
    'premium': {
        'whisper_models': ['tiny', 'base', 'small', 'medium', 'large'],
        'matching_engines': ['tfidf', 'neural', 'hybrid'],
        'sbert_models': ['all-MiniLM-L6-v2', 'all-mpnet-base-v2'],
        'max_file_size': 200 * 1024 * 1024,  # 200MB
        'daily_limit': None  # Unlimited
    }
}
```

---

## 🛠️ Development

### Project Structure

```
waveseek/
├── api/
│   └── api.py                 # Flask backend API
├── src/
│   ├── __init__.py
│   ├── audio_processor.py     # Audio preprocessing (Librosa)
│   ├── transcriber.py         # Whisper transcription
│   ├── text_processor.py      # Text cleaning & NLP
│   ├── matcher.py             # TF-IDF matching engine
│   ├── neural_matcher.py      # Neural embeddings matcher
│   └── database.py            # SQLite database management
├── waveseek-ui/
│   ├── src/
│   │   ├── App.tsx            # Main React application
│   │   └── ...
│   ├── package.json
│   └── ...
├── data/
│   ├── raw/csv/               # Input lyrics CSV files
│   ├── processed/             # SQLite database
│   └── audio_samples/         # Test audio files
├── models/
│   └── embeddings_cache/      # Cached neural embeddings
├── config.py                  # Configuration settings
├── main.py                    # CLI interface
├── setup_database.py          # Database initialization
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Running Tests

```bash
# Test audio processor
python src/audio_processor.py

# Test transcriber
python src/transcriber.py

# Test TF-IDF matcher
python src/matcher.py

# Test neural matcher
python src/neural_matcher.py

# Compare engines
python compare_matchers.py

# Run full demo
python demo.py
```

### Adding New Features

**1. New Matching Algorithm:**

```python
# src/custom_matcher.py
class CustomMatcher:
    def __init__(self):
        # Initialize your matcher
        pass
    
    def match(self, query_text, top_k=5):
        # Implement matching logic
        results = []
        # ... your algorithm ...
        return results
```

**2. Register in API:**

```python
# api/api.py
from src.custom_matcher import CustomMatcher

# In WaveSeekAPI.get_matcher()
elif engine == 'custom':
    self.matchers[cache_key] = CustomMatcher()
```

---

## 📊 Performance

### Benchmarks (100 test queries)

| Metric | TF-IDF | Neural | Hybrid |
|--------|--------|--------|--------|
| **Accuracy** | 67% | 84% | 87% |
| **Avg Confidence** | 42% | 68% | 71% |
| **Speed (cached)** | 35ms | 145ms | 168ms |
| **Speed (first run)** | 35ms | 2-5min* | 2-5min* |
| **Memory Usage** | 200MB | 450MB | 450MB |
| **Paraphrase Handling** | Poor | Excellent | Excellent |

*First run builds embeddings cache (one-time)

### Optimization Tips

**Speed:**
- Use TF-IDF for real-time applications
- Cache embeddings for neural matching
- Use smaller Whisper models (tiny/base)
- Enable GPU acceleration for Whisper

**Accuracy:**
- Use Neural or Hybrid engines
- Larger Whisper models (medium/large)
- Clean, high-quality audio input
- Sufficient training data in database

**Memory:**
- Free tier: ~2GB RAM minimum
- Premium tier: ~8GB RAM recommended
- Use `tiny` or `base` Whisper models
- Limit embeddings cache size

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? [Open an issue](https://github.com/AbdallahIsmaili/waveseek/issues)
- ✨ **Feature Requests**: Have an idea? [Suggest it](https://github.com/AbdallahIsmaili/waveseek/discussions)
- 📝 **Documentation**: Improve our docs
- 🔧 **Code**: Submit pull requests

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Code Style

- Python: Follow PEP 8
- React/TypeScript: Follow Airbnb style guide
- Add docstrings to all functions
- Include type hints where applicable
- Write unit tests for new features

### Testing

```bash
# Run Python tests
pytest tests/

# Run React tests
cd frontend && npm test

# Type checking
mypy src/
```

---

## 🗺️ Roadmap

### Phase 1: Song Recognition ✅ (Complete)
- [x] Whisper integration (all models)
- [x] TF-IDF matching
- [x] Neural embeddings (SBERT)
- [x] Hybrid approach
- [x] Web interface
- [x] Tier system
- [x] Batch processing
- [x] History tracking

### Phase 2: Voice Biometrics 🔄 (In Progress)
- [ ] Gender classification
- [ ] Age estimation
- [ ] Emotion detection
- [ ] Speaker identification
- [ ] Accent recognition
- [ ] Voice quality metrics

### Phase 3: Universal Sound Recognition 🔮 (Planned)
- [ ] Animal sound classification
- [ ] Mechanical sound identification
- [ ] Environmental audio analysis
- [ ] Multi-source detection
- [ ] Real-time streaming analysis
- [ ] Mobile app (iOS/Android)

### Future Enhancements
- [ ] Acoustic fingerprinting (Shazam-like)
- [ ] Humming/whistling recognition
- [ ] Live concert detection
- [ ] Karaoke mode
- [ ] API rate limiting & authentication
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Monitoring dashboard

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 WaveSeek AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - State-of-the-art speech recognition
- **Sentence-BERT** - Semantic text embeddings
- **Librosa** - Audio analysis library
- **React** - Frontend framework
- **Flask** - Backend framework
- All contributors and testers

---

## 📞 Support

- 📧 **Email**: ismaili.abdallah.me@gmail.com
<!-- - 💬 **Discord**: [Join our community](https://discord.gg/waveseek)
- 🐦 **Twitter**: [@WaveSeekAI](https://twitter.com/waveseekai)
- 📖 **Docs**: [Full Documentation](https://docs.waveseek-ai.com) -->
- 🐛 **Issues**: [GitHub Issues](https://github.com/AbdallahIsmaili/waveseek/issues)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AbdallahIsmaili/waveseek&type=Date)](https://star-history.com/#AbdallahIsmaili/waveseek&Date)

---

## 📈 Statistics

- **🎵 Songs in Database**: 5500+
- **🌍 Languages Supported**: 90+
- **⚡ Average Processing Time**: < 30 seconds
- **🎯 Average Accuracy**: 84% (Neural engine)
- **👥 Active Users**: Growing daily!

---

<div align="center">

**Made with ❤️ for the music and AI community**

[⬆ Back to Top](#-waveseek---multilingual-song-recognition-system)

</div>