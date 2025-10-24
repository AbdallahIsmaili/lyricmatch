"""
Audio processing module for LyricMatch
Handles audio loading, preprocessing, and noise reduction
"""
import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from config import Config


class AudioProcessor:
    """Process and prepare audio files for transcription"""
    
    def __init__(self, sample_rate=Config.SAMPLE_RATE):
        self.sample_rate = sample_rate
    
    def load_audio(self, audio_path, duration=None):
        """
        Load audio file and convert to mono
        
        Args:
            audio_path: Path to audio file
            duration: Maximum duration to load (in seconds)
        
        Returns:
            audio: numpy array of audio samples
            sr: sample rate
        """
        try:
            audio_path = Path(audio_path)
            
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Add .webm to supported formats check
            supported_formats = set(Config.SUPPORTED_FORMATS) | {'.webm'}
            
            # Check file format
            if audio_path.suffix.lower() not in supported_formats:
                raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
            
            # Load audio (librosa handles webm if ffmpeg is installed)
            audio, sr = librosa.load(
                audio_path,
                sr=self.sample_rate,
                mono=True,
                duration=duration or Config.AUDIO_DURATION_LIMIT
            )
            
            print(f"✅ Audio loaded: {audio_path.name}")
            print(f"   Duration: {len(audio) / sr:.2f}s | Sample Rate: {sr}Hz")
            
            return audio, sr
            
        except Exception as e:
            raise Exception(f"Error loading audio: {str(e)}")
    

    
    def reduce_noise(self, audio, sr):
        """
        Apply basic noise reduction techniques
        
        Args:
            audio: Audio signal
            sr: Sample rate
        
        Returns:
            Cleaned audio signal
        """
        # Trim silence from beginning and end
        audio_trimmed, _ = librosa.effects.trim(
            audio,
            top_db=20,  # Threshold in dB
            frame_length=2048,
            hop_length=512
        )
        
        # Normalize audio
        audio_normalized = librosa.util.normalize(audio_trimmed)
        
        return audio_normalized
    
    def convert_to_wav(self, input_path, output_path=None):
        """
        Convert audio file to WAV format
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output WAV file
        
        Returns:
            Path to converted WAV file
        """
        try:
            input_path = Path(input_path)
            
            if output_path is None:
                output_path = input_path.parent / f"{input_path.stem}_converted.wav"
            
            # Load audio with pydub
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            print(f"✅ Converted to WAV: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error converting audio: {str(e)}")
    
    def preprocess_audio(self, audio_path, apply_noise_reduction=True):
        """
        Complete preprocessing pipeline
        
        Args:
            audio_path: Path to audio file
            apply_noise_reduction: Whether to apply noise reduction
        
        Returns:
            Preprocessed audio signal and sample rate
        """
        # Load audio
        audio, sr = self.load_audio(audio_path)
        
        # Apply noise reduction if requested
        if apply_noise_reduction:
            audio = self.reduce_noise(audio, sr)
            print("✅ Noise reduction applied")
        
        return audio, sr
    
    def save_audio(self, audio, output_path, sr=None):
        """
        Save audio to file
        
        Args:
            audio: Audio signal
            output_path: Path to save file
            sr: Sample rate (uses default if None)
        """
        if sr is None:
            sr = self.sample_rate
        
        sf.write(output_path, audio, sr)
        print(f"✅ Audio saved: {output_path}")
    
    def get_audio_info(self, audio_path):
        """
        Get information about an audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with audio information
        """
        import soundfile as sf

        audio, sr = self.load_audio(audio_path)
        
        with sf.SoundFile(audio_path) as f:
            channels = f.channels
            subtype = f.subtype
        
        file_size = Path(audio_path).stat().st_size
        duration = len(audio) / sr
        bitrate = (file_size * 8) / duration / 1000  # kbps

        info = {
            'duration': len(audio) / sr,
            'sample_rate': sr,
            'channels': channels,
            'samples': len(audio),
            'format': Path(audio_path).suffix,
            'bitrate': round(bitrate, 1),  # NEW
            'file_size_mb': round(file_size / (1024*1024), 2),  # NEW
            'rms_energy': np.sqrt(np.mean(audio**2)),
            'max_amplitude': np.max(np.abs(audio))
        }
        
        return info


def test_audio_processor():
    """Test the audio processor"""
    print("\n" + "="*50)
    print("Testing Audio Processor")
    print("="*50 + "\n")
    
    processor = AudioProcessor()
    
    # Test with a sample audio file (you'll need to provide one)
    test_audio = Config.AUDIO_SAMPLES_DIR / "test.wav"
    
    if test_audio.exists():
        # Get audio info
        info = processor.get_audio_info(test_audio)
        print("\n📊 Audio Information:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Preprocess audio
        audio, sr = processor.preprocess_audio(test_audio)
        print(f"\n✅ Preprocessing complete: {len(audio)} samples")
    else:
        print(f"⚠️  No test audio found at: {test_audio}")
        print("   Place a test audio file there to test the processor")


if __name__ == "__main__":
    test_audio_processor()