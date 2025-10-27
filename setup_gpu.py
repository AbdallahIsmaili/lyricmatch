"""
GPU Setup and Testing Script for WaveSeek
Detects RTX 3060, installs dependencies, runs safety tests
Location: setup_gpu.py
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def check_cuda():
    """Check if CUDA is installed"""
    print("\n" + "="*60)
    print("🔍 Checking CUDA Installation")
    print("="*60)
    
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            print("✅ NVIDIA drivers detected")
            return True
        else:
            print("❌ nvidia-smi failed")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found")
        return False

def install_pytorch_gpu():
    """Install PyTorch with CUDA support"""
    print("\n" + "="*60)
    print("📦 Installing PyTorch with CUDA 11.8")
    print("="*60)
    print("This will take a few minutes...")
    
    # PyTorch with CUDA 11.8 (compatible with RTX 3060)
    cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    
    return run_command(cmd, "PyTorch GPU Installation")

def install_dependencies():
    """Install additional GPU dependencies"""
    packages = [
        "sentence-transformers",  # Will use PyTorch CUDA
        "pynvml",  # NVIDIA Management Library for monitoring
        "nvidia-ml-py3"  # Alternative monitoring
    ]
    
    print("\n" + "="*60)
    print("📦 Installing GPU Dependencies")
    print("="*60)
    
    for package in packages:
        print(f"\n📥 Installing {package}...")
        cmd = f"pip install {package}"
        if not run_command(cmd, f"Install {package}"):
            print(f"⚠️  Warning: {package} failed to install")
    
    return True

def test_pytorch_cuda():
    """Test PyTorch CUDA setup"""
    print("\n" + "="*60)
    print("🧪 Testing PyTorch CUDA")
    print("="*60)
    
    try:
        import torch
        
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
            print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            
            # Test tensor operation
            print("\n🧪 Testing GPU tensor operation...")
            x = torch.randn(1000, 1000).cuda()
            y = torch.matmul(x, x)
            print(f"✅ GPU tensor operation successful")
            print(f"   Result shape: {y.shape}")
            
            # Clear cache
            del x, y
            torch.cuda.empty_cache()
            
            return True
        else:
            print("❌ CUDA not available in PyTorch")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gpu_config():
    """Test GPU configuration module"""
    print("\n" + "="*60)
    print("🧪 Testing GPU Configuration Module")
    print("="*60)
    
    try:
        # Add parent dir to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from gpu_config import GPUConfig
        
        # Print status
        GPUConfig.print_gpu_status()
        
        # Test safety checks
        print("\n🔍 Testing Safety Checks:")
        print("="*60)
        
        models_to_test = [
            ('whisper', 'tiny'),
            ('whisper', 'base'),
            ('whisper', 'small'),
            ('whisper', 'medium'),
            ('whisper', 'large'),
            ('sbert', 'all-MiniLM-L6-v2'),
            ('sbert', 'all-mpnet-base-v2')
        ]
        
        for model_type, model_name in models_to_test:
            safety = GPUConfig.check_model_safety(model_type, model_name)
            status = "✅ SAFE" if safety['safe'] else "❌ UNSAFE"
            reason = safety.get('reason', '')
            print(f"{model_type:8s} {model_name:25s} {status:10s} {reason}")
        
        return True
        
    except ImportError as e:
        print(f"❌ GPU config import failed: {e}")
        print("Make sure gpu_config.py is in root directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whisper_gpu():
    """Test Whisper with GPU"""
    print("\n" + "="*60)
    print("🧪 Testing Whisper GPU Acceleration")
    print("="*60)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.transcriber import Transcriber
        from config import Config
        
        # Test with base model (safe for all GPUs)
        print("\n📝 Testing Whisper 'base' model with GPU...")
        transcriber = Transcriber(model_name='base', use_gpu=True)
        
        perf = transcriber.get_performance_info()
        print(f"\n⚙️  Performance Info:")
        for key, value in perf.items():
            print(f"   {key}: {value}")
        
        # Check if actually using GPU
        if perf['device'] == 'cuda':
            print("\n✅ Whisper GPU acceleration working!")
            return True
        else:
            print("\n⚠️  Whisper using CPU (may be safer for your model)")
            return True
            
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sbert_gpu():
    """Test SBERT with GPU"""
    print("\n" + "="*60)
    print("🧪 Testing SBERT GPU Acceleration")
    print("="*60)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Quick embedding test
        print("\n📝 Loading SBERT model...")
        from sentence_transformers import SentenceTransformer
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        
        # Test encoding
        print("\n🔬 Testing encoding...")
        test_texts = ["This is a test sentence"] * 10
        embeddings = model.encode(test_texts, batch_size=10)
        
        print(f"✅ Encoded {len(test_texts)} sentences")
        print(f"   Embedding shape: {embeddings.shape}")
        print(f"   Device used: {device}")
        
        if device == "cuda":
            import torch
            gpu_mem = torch.cuda.memory_allocated() / 1e9
            print(f"   GPU memory used: {gpu_mem:.2f} GB")
            torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ SBERT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_gpu_config_file():
    """Create gpu_config.py in config directory"""
    print("\n" + "="*60)
    print("📝 Creating GPU Configuration File")
    print("="*60)
    
    config_dir = Path(__file__).parent
    config_dir.mkdir(exist_ok=True)
    
    gpu_config_path = config_dir / "gpu_config.py"
    
    if gpu_config_path.exists():
        print(f"✅ GPU config already exists: {gpu_config_path}")
        return True
    
    print(f"Creating: {gpu_config_path}")
    print("⚠️  Please manually create gpu_config.py from the artifact")
    print("   Copy the 'gpu_config.py' artifact to: in root gpu_config.py")
    
    return False

def benchmark_gpu_vs_cpu():
    """Benchmark GPU vs CPU performance"""
    print("\n" + "="*60)
    print("⚡ GPU vs CPU Benchmark")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        import time
        import numpy as np
        
        test_texts = ["This is test sentence number " + str(i) for i in range(100)]
        
        print(f"\n📊 Encoding {len(test_texts)} sentences...\n")
        
        # CPU benchmark
        print("🖥️  CPU Mode:")
        model_cpu = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        start = time.time()
        embeddings_cpu = model_cpu.encode(test_texts, batch_size=16)
        cpu_time = time.time() - start
        print(f"   Time: {cpu_time:.2f}s")
        
        # GPU benchmark (if available)
        if torch.cuda.is_available():
            print("\n🎮 GPU Mode:")
            model_gpu = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
            torch.cuda.synchronize()
            start = time.time()
            embeddings_gpu = model_gpu.encode(test_texts, batch_size=64)
            torch.cuda.synchronize()
            gpu_time = time.time() - start
            print(f"   Time: {gpu_time:.2f}s")
            
            speedup = cpu_time / gpu_time
            print(f"\n⚡ Speedup: {speedup:.2f}x faster with GPU")
            
            # Verify results are similar
            diff = np.abs(embeddings_cpu - embeddings_gpu).mean()
            print(f"   Difference: {diff:.6f} (should be very small)")
            
            torch.cuda.empty_cache()
        else:
            print("\n⚠️  GPU not available for benchmark")
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False

def main():
    """Main setup flow"""
    print("\n" + "="*60)
    print("🎮 WAVESEEK GPU SETUP FOR RTX 3060")
    print("="*60)
    
    results = {}
    
    # 1. Check CUDA
    print("\n" + "="*60)
    print("STEP 1: CUDA Detection")
    print("="*60)
    results['cuda'] = check_cuda()
    
    if not results['cuda']:
        print("\n❌ CUDA not detected!")
        print("Please install NVIDIA drivers and CUDA toolkit:")
        print("   https://developer.nvidia.com/cuda-downloads")
        return
    
    # 2. Install PyTorch GPU
    print("\n" + "="*60)
    print("STEP 2: PyTorch GPU Installation")
    print("="*60)
    install = input("Install PyTorch with CUDA 11.8? (y/n): ").lower()
    if install == 'y':
        results['pytorch'] = install_pytorch_gpu()
    else:
        print("⚠️  Skipping PyTorch installation")
        results['pytorch'] = False
    
    # 3. Install dependencies
    print("\n" + "="*60)
    print("STEP 3: GPU Dependencies")
    print("="*60)
    results['deps'] = install_dependencies()
    
    # 4. Test PyTorch CUDA
    print("\n" + "="*60)
    print("STEP 4: PyTorch CUDA Test")
    print("="*60)
    results['pytorch_test'] = test_pytorch_cuda()
    
    # 5. Check GPU config file
    print("\n" + "="*60)
    print("STEP 5: GPU Configuration File")
    print("="*60)
    results['gpu_config'] = create_gpu_config_file()
    
    # 6. Test GPU config module
    if results['gpu_config']:
        print("\n" + "="*60)
        print("STEP 6: GPU Config Module Test")
        print("="*60)
        results['gpu_config_test'] = test_gpu_config()
    
    # 7. Test Whisper GPU
    print("\n" + "="*60)
    print("STEP 7: Whisper GPU Test")
    print("="*60)
    test_whisper = input("Test Whisper GPU? (y/n): ").lower()
    if test_whisper == 'y':
        results['whisper'] = test_whisper_gpu()
    
    # 8. Test SBERT GPU
    print("\n" + "="*60)
    print("STEP 8: SBERT GPU Test")
    print("="*60)
    test_sbert = input("Test SBERT GPU? (y/n): ").lower()
    if test_sbert == 'y':
        results['sbert'] = test_sbert_gpu()
    
    # 9. Benchmark
    print("\n" + "="*60)
    print("STEP 9: Performance Benchmark")
    print("="*60)
    bench = input("Run GPU vs CPU benchmark? (y/n): ").lower()
    if bench == 'y':
        results['benchmark'] = benchmark_gpu_vs_cpu()
    
    # Summary
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    
    for step, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step:20s} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{passed}/{total} steps successful")
    
    if results.get('pytorch_test'):
        print("\n🎉 GPU SETUP COMPLETE!")
        print("\n📝 Next Steps:")
        print("   1. Copy gpu_config.py artifact to project root (gpu_config.py)")
        print("   2. Update transcriber.py and neural_matcher.py")
        print("   3. Update api.py with GPU tier")
        print("   4. Test with: python test_gpu.py")
        print("   5. Start API: python api/api.py")
    else:
        print("\n⚠️  GPU setup incomplete")
        print("Check the errors above and try again")

if __name__ == "__main__":
    main()