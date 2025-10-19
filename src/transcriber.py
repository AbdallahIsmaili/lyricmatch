"""
Speech-to-text transcription module using OpenAI Whisper
Enhanced with automatic language detection for multilingual support
"""
import whisper
import torch
import warnings
warnings.filterwarnings('ignore')

from config import Config
from src.audio_processor import AudioProcessor


class Transcriber:
    """Transcribe audio to text using Whisper with multilingual support"""
    
    def __init__(self, model_name=Config.WHISPER_MODEL):
        """
        Initialize Whisper model
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🔄 Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name, device=self.device)
        print(f"✅ Whisper model loaded successfully")
        
        self.audio_processor = AudioProcessor()
    
    def transcribe(self, audio_path, language=Config.WHISPER_LANGUAGE, verbose=False):
        """
        Transcribe audio file to text with automatic language detection
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', 'ko', 'ja') or None for auto-detect
            verbose: Print detailed transcription info
        
        Returns:
            Dictionary containing transcription results
        """
        try:
            print(f"\n🎤 Transcribing: {audio_path}")
            
            # Handle language parameter - convert empty string or "none" to None
            if language and language.lower() in ['none', 'null', '']:
                language = None
            
            # Build transcription parameters
            transcribe_params = {
                'fp16': False,  # Disable fp16 for CPU compatibility
                'verbose': verbose
            }
            
            # Only add language if specified (let Whisper auto-detect if None)
            if language:
                transcribe_params['language'] = language
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                str(audio_path),
                **transcribe_params
            )
            
            # Extract detected language (Whisper always detects it)
            detected_language = result.get('language', 'unknown')
            
            transcription = {
                'text': result['text'].strip(),
                'language': detected_language,
                'language_probability': result.get('language_probability', 0.0),
                'segments': result.get('segments', []),
                'duration': sum(seg['end'] - seg['start'] for seg in result.get('segments', []))
            }
            
            print(f"✅ Transcription complete!")
            print(f"   Language: {transcription['language']} (confidence: {transcription['language_probability']:.2%})")
            print(f"   Duration: {transcription['duration']:.2f}s")
            print(f"   Text length: {len(transcription['text'])} characters")
            
            if transcription['text']:
                print(f"\n📝 Transcribed text:\n   \"{transcription['text'][:200]}...\"")
            else:
                print("⚠️  Warning: No text was transcribed")
            
            return transcription
            
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    def detect_language(self, audio_path):
        """
        Detect the language of an audio file without full transcription
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with language code and probability
        """
        try:
            # Load audio
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return {
                'language': detected_language,
                'probability': probs[detected_language],
                'all_probabilities': dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            raise Exception(f"Language detection error: {str(e)}")
    
    def transcribe_with_preprocessing(self, audio_path, apply_noise_reduction=True, language=None):
        """
        Preprocess audio and then transcribe
        
        Args:
            audio_path: Path to audio file
            apply_noise_reduction: Apply noise reduction before transcription
            language: Language code or None for auto-detection
        
        Returns:
            Transcription results
        """
        # Preprocess audio
        audio, sr = self.audio_processor.preprocess_audio(
            audio_path,
            apply_noise_reduction=apply_noise_reduction
        )
        
        # Save preprocessed audio temporarily
        temp_path = Config.AUDIO_SAMPLES_DIR / "temp_preprocessed.wav"
        self.audio_processor.save_audio(audio, temp_path, sr)
        
        # Transcribe
        result = self.transcribe(temp_path, language=language)
        
        # Clean up temp file
        temp_path.unlink(missing_ok=True)
        
        return result
    
    def transcribe_segment(self, audio_path, start_time=None, end_time=None, language=None):
        """
        Transcribe a specific segment of audio
        
        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            language: Language code or None for auto-detection
        
        Returns:
            Transcription of the segment
        """
        # Load audio segment
        audio, sr = self.audio_processor.load_audio(audio_path)
        
        if start_time is not None or end_time is not None:
            start_sample = int(start_time * sr) if start_time else 0
            end_sample = int(end_time * sr) if end_time else len(audio)
            audio = audio[start_sample:end_sample]
        
        # Save segment temporarily
        temp_path = Config.AUDIO_SAMPLES_DIR / "temp_segment.wav"
        self.audio_processor.save_audio(audio, temp_path, sr)
        
        # Transcribe
        result = self.transcribe(temp_path, language=language)
        
        # Clean up
        temp_path.unlink(missing_ok=True)
        
        return result
    
    def get_detailed_transcription(self, audio_path, language=None):
        """
        Get detailed transcription with word-level timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detection
        
        Returns:
            Detailed transcription with segments and timestamps
        """
        result = self.transcribe(audio_path, language=language, verbose=True)
        
        detailed_output = {
            'full_text': result['text'],
            'language': result['language'],
            'language_probability': result['language_probability'],
            'segments': []
        }
        
        for segment in result['segments']:
            detailed_output['segments'].append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'confidence': segment.get('avg_logprob', 0)
            })
        
        return detailed_output


def test_transcriber():
    """Test the transcriber with multilingual support"""
    print("\n" + "="*50)
    print("Testing Transcriber (Multilingual)")
    print("="*50 + "\n")
    
    # Initialize transcriber
    transcriber = Transcriber(model_name="base")
    
    # Test with sample audio
    test_audio = Config.AUDIO_SAMPLES_DIR / "test.wav"
    
    if test_audio.exists():
        # Detect language first
        print("🔍 Detecting language...")
        lang_info = transcriber.detect_language(test_audio)
        print(f"   Detected: {lang_info['language']} ({lang_info['probability']:.2%})")
        print(f"   Top 5 languages:")
        for lang, prob in list(lang_info['all_probabilities'].items())[:5]:
            print(f"      {lang}: {prob:.2%}")
        
        # Basic transcription (auto-detect)
        print("\n" + "="*50)
        result = transcriber.transcribe(test_audio)
        
        print("\n" + "="*50)
        print("Transcription Result:")
        print("="*50)
        print(f"Text: {result['text']}")
        print(f"Language: {result['language']}")
        print(f"Confidence: {result['language_probability']:.2%}")
        print(f"Duration: {result['duration']:.2f}s")
        
    else:
        print(f"⚠️  No test audio found at: {test_audio}")
        print("   Place a test audio file (with singing/speech) there to test")
        print("\n💡 Available Whisper models:")
        print("   - tiny:   Fast, lower accuracy")
        print("   - base:   Balanced (recommended)")
        print("   - small:  Better accuracy, slower")
        print("   - medium: High accuracy, slow")
        print("   - large:  Best accuracy, very slow")
        print("\n🌍 Supported languages include:")
        print("   English (en), Spanish (es), French (fr), German (de),")
        print("   Korean (ko), Japanese (ja), Chinese (zh), and 90+ more!")


if __name__ == "__main__":
    test_transcriber()