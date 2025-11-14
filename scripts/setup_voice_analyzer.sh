#!/bin/bash
# Setup script for Production Voice Analyzer
# Location: scripts/setup_voice_analyzer.sh

echo "=================================================="
echo "  WaveSeek Production Voice Analyzer Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"
echo ""

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install librosa numpy scipy scikit-learn soundfile
echo "   ✅ Core dependencies installed"
echo ""

# Install Silero VAD
echo "📦 Installing Silero VAD (Voice Activity Detection)..."
pip install silero-vad
# It will also auto-download via torch.hub on first use
echo "   ✅ Silero VAD installed"
echo ""

# Install Pyannote (optional but recommended)
echo "📦 Installing Pyannote Audio (Speaker Diarization)..."
echo "   ⚠️  This requires a FREE Hugging Face account"
echo ""
read -p "   Do you have a Hugging Face token? (y/n): " has_token

if [ "$has_token" = "y" ] || [ "$has_token" = "Y" ]; then
    pip install pyannote.audio
    echo ""
    echo "   ✅ Pyannote installed"
    echo ""
    echo "=================================================="
    echo "  🔑 NEXT STEPS:"
    echo "=================================================="
    echo ""
    echo "1. Get your Hugging Face token:"
    echo "   https://huggingface.co/settings/tokens"
    echo ""
    echo "2. Accept model terms:"
    echo "   https://huggingface.co/pyannote/speaker-diarization-3.1"
    echo ""
    echo "3. Set your token in voice_analyzer.py (line 55):"
    echo "   HF_TOKEN = 'hf_LzjdhaMlfaOJMGOCqvcFxKIIKGQrRmyXSpREMOVE_THIS_FROM_SAMPLE_TOKEN'"
    echo ""
    echo "   OR set environment variable:"
    echo "   export HF_TOKEN='hf_LzjdhaMlfaOJMGOCqvcFxKIIKGQrRmyXSpREMOVE_THIS_FROM_SAMPLE_TOKEN'"
    echo ""
else
    echo ""
    echo "   ℹ️  Skipping Pyannote installation"
    echo "   You can install it later with: pip install pyannote.audio"
    echo ""
    echo "   The analyzer will use fallback methods without Pyannote."
    echo "   For production accuracy, we recommend installing it."
    echo ""
    echo "   To get started:"
    echo "   1. Sign up at: https://huggingface.co/join"
    echo "   2. Get token at: https://huggingface.co/settings/tokens"
    echo "   3. Run this script again"
    echo ""
fi

echo "=================================================="
echo "  ✅ Setup complete!"
echo "=================================================="
echo ""
echo "🧪 Test the analyzer:"
echo "   python -c 'from src.voice_analyzer import VoiceAnalyzer; VoiceAnalyzer()'"
echo ""