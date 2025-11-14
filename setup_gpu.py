"""
Windows GPU Setup and Detection Script
Tests CUDA availability and model compatibility
Location: setup_gpu_windows.py
"""
import subprocess
import sys
import os
from pathlib import Path


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_python_version():
    """Check Python version"""
    print_section("PYTHON VERSION CHECK")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False


def check_nvidia_driver():
    """Check NVIDIA driver using nvidia-smi"""
    print_section("NVIDIA DRIVER CHECK")
    
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ NVIDIA driver detected")
            
            # Parse GPU name
            for line in result.stdout.split('\n'):
                if 'GeForce' in line or 'RTX' in line or 'GTX' in line:
                    print(f"\n🎮 GPU Found: {line.strip()}")
            
            return True
        else:
            print("❌ nvidia-smi failed")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ nvidia-smi not found")
        print("\n💡 Please install NVIDIA drivers:")
        print("   https://www.nvidia.com/Download/index.aspx")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_cuda_pytorch():
    """Check if PyTorch has CUDA support"""
    print_section("PYTORCH CUDA CHECK")
    
    try:
        import torch
        
        print(f"✅ PyTorch installed: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   cuDNN version: {torch.backends.cudnn.version()}")
            print(f"   Number of GPUs: {torch.cuda.device_count()}")
            
            # Get GPU info
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9
                print(f"\n   GPU {i}: {gpu_name}")
                print(f"   Memory: {gpu_memory:.2f} GB")
            
            # Test GPU operation
            print("\n🧪 Testing GPU tensor operation...")
            try:
                x = torch.randn(100, 100).cuda()
                y = torch.matmul(x, x)
                print(f"   ✅ GPU operation successful")
                
                # Cleanup
                del x, y
                torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"   ❌ GPU operation failed: {e}")
                return False
            
            return True
        else:
            print("\n❌ CUDA not available in PyTorch")
            print("\n💡 Install PyTorch with CUDA:")
            print("   pip uninstall torch torchvision torchaudio")
            print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        print("\n💡 Install PyTorch:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False


def check_gpu_config():
    """Check if gpu_config.py exists and works"""
    print_section("GPU CONFIGURATION MODULE")
    
    try:
        # Add current dir to path
        sys.path.insert(0, str(Path.cwd()))
        
        from gpu_config import GPUConfig
        
        print("✅ gpu_config.py found")
        
        # Show GPU status
        GPUConfig.print_gpu_status()
        
        return True
        
    except ImportError:
        print("⚠️  gpu_config.py not found")
        print("\n💡 Create gpu_config.py in project root")
        print("   Copy the artifact 'Fixed GPU Config' to: gpu_config.py")
        return False
    except Exception as e:
        print(f"❌ Error loading gpu_config: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_safety():
    """Test model safety checks"""
    print_section("MODEL SAFETY CHECKS")
    
    try:
        from gpu_config import GPUConfig
        
        print("Checking which models are safe for your GPU:\n")
        
        # Whisper models
        print("🎤 Whisper Models:")
        print(f"{'Model':<15} {'VRAM Need':<12} {'Safe?':<10} {'Notes'}")
        print("-" * 70)
        
        for model in ['tiny', 'base', 'small', 'medium', 'large']:
            safety = GPUConfig.check_model_safety('whisper', model)
            safe = "✅ YES" if safety['safe'] else "❌ NO"
            vram = GPUConfig.WHISPER_MODEL_LIMITS[model]['vram_mb'] / 1000
            reason = safety.get('reason', '')[:40] if not safety['safe'] else 'Safe to use'
            
            print(f"{model:<15} {vram:.1f}GB        {safe:<10} {reason}")
        
        # SBERT models
        print(f"\n🧠 SBERT Models:")
        print(f"{'Model':<30} {'VRAM Need':<12} {'Safe?'}")
        print("-" * 70)
        
        sbert_models = [
            'all-MiniLM-L6-v2',
            'all-mpnet-base-v2',
            'all-MiniLM-L12-v2'
        ]
        
        for model in sbert_models:
            if model in GPUConfig.SBERT_MODEL_LIMITS:
                safety = GPUConfig.check_model_safety('sbert', model)
                safe = "✅ YES" if safety['safe'] else "❌ NO"
                vram = GPUConfig.SBERT_MODEL_LIMITS[model]['vram_mb'] / 1000
                
                print(f"{model:<30} {vram:.1f}GB        {safe}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_whisper_gpu():
    """Test Whisper GPU acceleration"""
    print_section("WHISPER GPU TEST")
    
    answer = input("Test Whisper GPU? This will download the model. (y/n): ").lower()
    
    if answer != 'y':
        print("⏭️  Skipped")
        return None
    
    try:
        print("\n🔄 Loading Whisper base model...")
        
        from src.transcriber import Transcriber
        
        transcriber = Transcriber(model_name='base', use_gpu=True)
        
        perf = transcriber.get_performance_info()
        
        print("\n⚙️  Performance Info:")
        for key, value in perf.items():
            print(f"   {key}: {value}")
        
        if perf['device'] == 'cuda':
            print("\n✅ Whisper GPU acceleration WORKING!")
            return True
        else:
            print("\n⚠️  Whisper using CPU")
            print("   Check gpu_config.py safety limits")
            return False
            
    except Exception as e:
        print(f"\n❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sbert_gpu():
    """Test SBERT GPU acceleration"""
    print_section("SBERT GPU TEST")
    
    answer = input("Test SBERT GPU? This will download the model. (y/n): ").lower()
    
    if answer != 'y':
        print("⏭️  Skipped")
        return None
    
    try:
        print("\n🔄 Loading SBERT model...")
        
        import torch
        from sentence_transformers import SentenceTransformer
        import time
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Device: {device}")
        
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        
        # Test encoding
        test_texts = ["This is a test sentence"] * 20
        
        print(f"\n🧪 Encoding {len(test_texts)} sentences...")
        
        start = time.time()
        embeddings = model.encode(test_texts, batch_size=20)
        elapsed = time.time() - start
        
        print(f"   ✅ Encoded in {elapsed:.2f}s")
        print(f"   Embedding shape: {embeddings.shape}")
        
        if device == "cuda":
            gpu_mem = torch.cuda.memory_allocated() / 1e9
            print(f"   GPU memory used: {gpu_mem:.2f} GB")
            torch.cuda.empty_cache()
            print("\n✅ SBERT GPU acceleration WORKING!")
            return True
        else:
            print("\n⚠️  SBERT using CPU")
            return False
            
    except Exception as e:
        print(f"\n❌ SBERT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def benchmark_gpu_cpu():
    """Benchmark GPU vs CPU performance"""
    print_section("GPU vs CPU BENCHMARK")
    
    answer = input("Run performance benchmark? (y/n): ").lower()
    
    if answer != 'y':
        print("⏭️  Skipped")
        return None
    
    try:
        import torch
        from sentence_transformers import SentenceTransformer
        import time
        import numpy as np
        
        test_texts = ["Test sentence number " + str(i) for i in range(100)]
        
        print(f"\n📊 Encoding {len(test_texts)} sentences...\n")
        
        # CPU test
        print("🖥️  CPU Mode:")
        model_cpu = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        start = time.time()
        emb_cpu = model_cpu.encode(test_texts, batch_size=16, show_progress_bar=False)
        cpu_time = time.time() - start
        print(f"   Time: {cpu_time:.2f}s")
        
        # GPU test
        if torch.cuda.is_available():
            print("\n🎮 GPU Mode:")
            model_gpu = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
            torch.cuda.synchronize()
            start = time.time()
            emb_gpu = model_gpu.encode(test_texts, batch_size=64, show_progress_bar=False)
            torch.cuda.synchronize()
            gpu_time = time.time() - start
            print(f"   Time: {gpu_time:.2f}s")
            
            speedup = cpu_time / gpu_time
            print(f"\n⚡ Speedup: {speedup:.2f}x faster with GPU")
            
            # Verify similarity
            diff = np.abs(emb_cpu - emb_gpu).mean()
            print(f"   Difference: {diff:.6f} (should be <0.001)")
            
            torch.cuda.empty_cache()
            return True
        else:
            print("\n⚠️  GPU not available for benchmark")
            return False
            
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_recommendations(results):
    """Show recommendations based on test results"""
    print_section("RECOMMENDATIONS")
    
    has_gpu = results.get('nvidia_driver', False) and results.get('pytorch_cuda', False)
    
    if has_gpu:
        print("✅ GPU Setup Complete!\n")
        print("📝 Recommended Configuration:\n")
        
        print("1️⃣  For Whisper (transcription):")
        if results.get('whisper_test'):
            print("   ✅ Use GPU: python main.py audio.wav")
        else:
            print("   ⚠️  Use CPU (safer): python main.py audio.wav --no-gpu")
        
        print("\n2️⃣  For SBERT (matching):")
        if results.get('sbert_test'):
            print("   ✅ GPU acceleration enabled automatically")
        else:
            print("   ⚠️  Will use CPU (check gpu_config.py)")
        
        print("\n3️⃣  Config file:")
        if results.get('gpu_config'):
            print("   ✅ gpu_config.py is properly configured")
        else:
            print("   ⚠️  Create gpu_config.py from artifact")
        
        print("\n🚀 Next Steps:")
        print("   1. Test full pipeline: python main.py data/audio_samples/test.wav")
        print("   2. Monitor GPU usage: watch -n 1 nvidia-smi")
        print("   3. Check temperatures during use")
        
    else:
        print("⚠️  GPU Not Available\n")
        print("💡 Options:")
        print("   1. Install NVIDIA drivers")
        print("   2. Install CUDA toolkit")
        print("   3. Install PyTorch with CUDA:")
        print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("\n   OR use CPU mode (slower but works):")
        print("      python main.py audio.wav --force-cpu")


def main():
    """Main setup flow"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        WAVESEEK GPU SETUP - WINDOWS                                ║
║        Automated GPU Detection and Configuration                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Run checks
    results['python'] = check_python_version()
    results['nvidia_driver'] = check_nvidia_driver()
    results['pytorch_cuda'] = check_cuda_pytorch()
    results['gpu_config'] = check_gpu_config()
    
    # Only test models if GPU is available
    if results['pytorch_cuda'] and results['gpu_config']:
        results['model_safety'] = test_model_safety()
        results['whisper_test'] = test_whisper_gpu()
        results['sbert_test'] = test_sbert_gpu()
        results['benchmark'] = benchmark_gpu_cpu()
    
    # Summary
    print_section("SETUP SUMMARY")
    
    print(f"{'Check':<25} {'Status'}")
    print("-" * 70)
    
    for key, value in results.items():
        if value is True:
            status = "✅ PASS"
        elif value is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIPPED"
        
        label = key.replace('_', ' ').title()
        print(f"{label:<25} {status}")
    
    # Recommendations
    show_recommendations(results)
    
    print("\n" + "="*70)
    print("  SETUP COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()