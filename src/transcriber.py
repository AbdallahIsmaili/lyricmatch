"""
Speech-to-text transcription module using OpenAI Whisper
Enhanced with GPU acceleration and safety monitoring
Location: src/transcriber.py (UPDATED)
"""
import whisper
import torch
import warnings
import time
warnings.filterwarnings('ignore')

from config import Config

# Import GPU config (create this file from the artifact above)
try:
    from gpu_config import GPUConfig
    GPU_AVAILABLE = True
except ImportError:
    print("⚠️  GPU config not found - using CPU mode")
    GPU_AVAILABLE = False
    class GPUConfig:  # Fallback
        DEVICE = "cpu"
        WHISPER_FP16 = False


class Transcriber:
    """Transcribe audio to text using Whisper with GPU acceleration"""
    
    def __init__(self, model_name=Config.WHISPER_MODEL, use_gpu=True, force_cpu=False):
        """
        Initialize Whisper model with GPU support
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            use_gpu: Attempt to use GPU if available
            force_cpu: Force CPU mode even if GPU available
        """
        self.model_name = model_name
        self.use_gpu = use_gpu and GPU_AVAILABLE and not force_cpu
        
        # Determine device
        if force_cpu:
            self.device = "cpu"
            self.use_fp16 = False
            print("🖥️  Forced CPU mode")
        elif self.use_gpu:
            # Check safety
            safety = GPUConfig.check_model_safety('whisper', model_name)
            
            if safety.get('safe', False):
                self.device = GPUConfig.DEVICE
                self.use_fp16 = GPUConfig.WHISPER_FP16 and self.device == "cuda"
                print(f"🎮 GPU mode enabled for Whisper '{model_name}'")
                print(f"   Device: {self.device}")
                print(f"   FP16: {self.use_fp16}")
                if 'memory_needed_gb' in safety:
                    print(f"   VRAM needed: ~{safety['memory_needed_gb']:.1f}GB")
            else:
                self.device = "cpu"
                self.use_fp16 = False
                print(f"⚠️  GPU unsafe for '{model_name}': {safety.get('reason', 'Unknown')}")
                print(f"   Falling back to CPU")
        else:
            self.device = "cpu"
            self.use_fp16 = False
        
        # Load model
        print(f"📄 Loading Whisper model '{model_name}' on {self.device}...")
        start_time = time.time()
        
        self.model = whisper.load_model(model_name, device=self.device)
        
        load_time = time.time() - start_time
        print(f"✅ Whisper model loaded in {load_time:.2f}s")
        
        # Print GPU status if using GPU
        if self.device == "cuda" and GPU_AVAILABLE:
            gpu_info = GPUConfig.get_gpu_info()
            print(f"   VRAM allocated: {gpu_info['memory_allocated_gb']:.2f}GB")
            if gpu_info.get('temperature_c'):
                print(f"   GPU temp: {gpu_info['temperature_c']}°C")
    
    def transcribe(self, audio_path, language=Config.WHISPER_LANGUAGE, verbose=False):
        """
        Transcribe audio file with GPU acceleration
        
        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detect
            verbose: Print detailed info
        
        Returns:
            Dictionary with transcription results
        """
        try:
            print(f"\n🎤 Transcribing: {audio_path}")
            
            # Monitor GPU before transcription
            if self.device == "cuda" and GPU_AVAILABLE:
                gpu_info = GPUConfig.get_gpu_info()
                temp = gpu_info.get('temperature_c')
                if temp is not None and temp > GPUConfig.THROTTLE_TEMP:
                    print(f"⚠️  GPU hot ({gpu_info['temperature_c']}°C), waiting to cool...")
                    time.sleep(5)
            
            # Handle language parameter
            if language and language.lower() in ['none', 'null', '']:
                language = None
            
            # Build transcription parameters
            transcribe_params = {
                'fp16': self.use_fp16,  # Enable FP16 on GPU
                'verbose': verbose
            }
            
            if language:
                transcribe_params['language'] = language
            
            # Transcribe with timing
            start_time = time.time()
            
            result = self.model.transcribe(
                str(audio_path),
                **transcribe_params
            )
            
            transcribe_time = time.time() - start_time
            
            # Extract results
            detected_language = result.get('language', 'unknown')
            
            transcription = {
                'text': result['text'].strip(),
                'language': detected_language,
                'language_probability': result.get('language_probability', 0.0),
                'segments': result.get('segments', []),
                'duration': sum(seg['end'] - seg['start'] for seg in result.get('segments', [])),
                'processing_time': transcribe_time,
                'device_used': self.device,
                'fp16_used': self.use_fp16
            }
            
            # Performance metrics
            audio_duration = transcription['duration']
            rtf = transcribe_time / audio_duration if audio_duration > 0 else 0
            
            print(f"✅ Transcription complete!")
            print(f"   Language: {transcription['language']} ({transcription['language_probability']:.2%})")
            print(f"   Duration: {transcription['duration']:.2f}s")
            print(f"   Processing: {transcribe_time:.2f}s (RTF: {rtf:.2f}x)")
            print(f"   Device: {self.device} (FP16: {self.use_fp16})")
            
            # GPU stats after transcription
            if self.device == "cuda" and GPU_AVAILABLE:
                gpu_info = GPUConfig.get_gpu_info()
                print(f"   VRAM used: {gpu_info['memory_allocated_gb']:.2f}GB")
                temp = gpu_info.get('temperature_c')
                if temp is not None:
                    print(f"   GPU temp: {temp}°C")

            if transcription['text']:
                print(f"\n📝 Text: \"{transcription['text'][:200]}...\"")
            else:
                print("⚠️  Warning: No text transcribed")
            
            return transcription
            
        except Exception as e:
            # Clear GPU cache on error
            if self.device == "cuda":
                GPUConfig.clear_gpu_cache()
            
            raise Exception(f"Transcription error: {str(e)}")
    
    def detect_language(self, audio_path):
        """Detect language without full transcription"""
        try:
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            return {
                'language': detected_language,
                'probability': probs[detected_language],
                'all_probabilities': dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            raise Exception(f"Language detection error: {str(e)}")
    
    def get_performance_info(self):
        """Get current performance configuration"""
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'fp16_enabled': self.use_fp16,
            'gpu_available': GPU_AVAILABLE
        }
        
        if self.device == "cuda" and GPU_AVAILABLE:
            gpu_info = GPUConfig.get_gpu_info()
            info['gpu_name'] = gpu_info.get('name', 'Unknown')
            info['vram_allocated_gb'] = gpu_info.get('memory_allocated_gb', 0)
            info['vram_free_gb'] = gpu_info.get('memory_free_gb', 0)
            info['temperature_c'] = gpu_info.get('temperature_c')
        
        return info
    
    def cleanup(self):
        """Clean up GPU resources"""
        if self.device == "cuda" and GPU_AVAILABLE:
            del self.model
            GPUConfig.clear_gpu_cache()
            print("🧹 GPU cache cleared")


def test_transcriber():
    """Test transcriber with GPU support"""
    print("\n" + "="*60)
    print("Testing GPU-Accelerated Transcriber")
    print("="*60 + "\n")
    
    # Show GPU status
    if GPU_AVAILABLE:
        GPUConfig.print_gpu_status()
    
    # Test with base model (safe for all GPUs)
    transcriber = Transcriber(model_name="base", use_gpu=True)
    
    # Show performance info
    perf_info = transcriber.get_performance_info()
    print(f"\n⚙️  Performance Configuration:")
    for key, value in perf_info.items():
        print(f"   {key}: {value}")
    
    # Test audio if available
    from config import Config
    test_audio = Config.AUDIO_SAMPLES_DIR / "test.wav"
    
    if test_audio.exists():
        print("\n" + "="*60)
        result = transcriber.transcribe(test_audio)
        print("\n" + "="*60)
        print("Results:")
        print(f"  Text: {result['text']}")
        print(f"  Processing Time: {result['processing_time']:.2f}s")
        print(f"  Device: {result['device_used']}")
    else:
        print(f"\n⚠️  No test audio at: {test_audio}")
    
    # Cleanup
    transcriber.cleanup()


if __name__ == "__main__":
    test_transcriber()