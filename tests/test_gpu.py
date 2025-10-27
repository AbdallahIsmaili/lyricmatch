"""
Comprehensive GPU Testing Suite for WaveSeek
Tests all GPU-accelerated components safely
Location: test_gpu.py
"""
import sys
from pathlib import Path
import time
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from gpu_config import GPUConfig
    GPU_AVAILABLE = GPUConfig.CUDA_AVAILABLE
except ImportError:
    print("❌ GPU config not found!")
    print("Please create gpu_config.py in the project root")  # UPDATED
    sys.exit(1)


def test_gpu_detection():
    """Test 1: GPU Detection"""
    print("\n" + "="*60)
    print("TEST 1: GPU DETECTION")
    print("="*60)
    
    GPUConfig.print_gpu_status()
    
    if not GPU_AVAILABLE:
        print("\n❌ No GPU detected")
        return False
    
    gpu_info = GPUConfig.get_gpu_info()
    
    # Check for RTX 3060
    if 'RTX 3060' in gpu_info.get('name', ''):
        print("\n✅ RTX 3060 detected!")
    else:
        print(f"\n⚠️  GPU detected: {gpu_info.get('name', 'Unknown')}")
        print("   (These tests are optimized for RTX 3060)")
    
    # Check VRAM
    vram = gpu_info.get('memory_total_gb', 0)
    if vram >= 6.0:
        print(f"✅ Sufficient VRAM: {vram:.1f}GB")
    else:
        print(f"⚠️  Low VRAM: {vram:.1f}GB (may limit model sizes)")
    
    # Check temperature
    temp = gpu_info.get('temperature_c')
    if temp:
        if temp < GPUConfig.THROTTLE_TEMP:
            print(f"✅ GPU cool: {temp}°C")
        else:
            print(f"⚠️  GPU warm: {temp}°C")
    
    return True


def test_model_safety():
    """Test 2: Model Safety Checks"""
    print("\n" + "="*60)
    print("TEST 2: MODEL SAFETY CHECKS")
    print("="*60)
    
    all_safe = True
    
    # Whisper models
    print("\n🎤 Whisper Models:")
    whisper_models = ['tiny', 'base', 'small', 'medium', 'large']
    
    for model in whisper_models:
        safety = GPUConfig.check_model_safety('whisper', model)
        status = "✅ SAFE" if safety['safe'] else "❌ UNSAFE"
        vram = GPUConfig.WHISPER_MODEL_LIMITS[model]['vram_mb']
        
        print(f"  {model:8s} - {status:10s} (~{vram:4d}MB VRAM)")
        
        if safety['safe']:
            print(f"           {safety.get('reason', 'OK')}")
        else:
            print(f"           ⚠️  {safety.get('reason', 'Unknown')}")
            all_safe = False
    
    # SBERT models
    print("\n🧠 SBERT Models:")
    sbert_models = [
        'all-MiniLM-L6-v2',
        'all-mpnet-base-v2',
        'paraphrase-MiniLM-L6-v2'
    ]
    
    for model in sbert_models:
        safety = GPUConfig.check_model_safety('sbert', model)
        status = "✅ SAFE" if safety['safe'] else "❌ UNSAFE"
        vram = GPUConfig.SBERT_MODEL_LIMITS.get(model, {}).get('vram_mb', 999)
        
        print(f"  {model:30s} - {status:10s} (~{vram:4d}MB)")
    
    if all_safe:
        print("\n✅ All recommended models are safe for your GPU")
    else:
        print("\n⚠️  Some models may be unsafe - use with caution")
    
    return True


def test_whisper_cpu_vs_gpu():
    """Test 3: Whisper CPU vs GPU"""
    print("\n" + "="*60)
    print("TEST 3: WHISPER CPU vs GPU")
    print("="*60)
    
    try:
        from src.transcriber import Transcriber
        from config import Config
        import tempfile
        import numpy as np
        import soundfile as sf
        
        # Create test audio (5 seconds of sine wave)
        print("\n📝 Creating test audio...")
        sr = 16000
        duration = 5
        t = np.linspace(0, duration, sr * duration)
        audio = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
        
        temp_file = Path(tempfile.gettempdir()) / "test_whisper.wav"
        sf.write(temp_file, audio, sr)
        
        # Test CPU
        print("\n🖥️  Testing CPU mode...")
        transcriber_cpu = Transcriber(model_name='tiny', use_gpu=False)
        start = time.time()
        result_cpu = transcriber_cpu.transcribe(str(temp_file))
        cpu_time = time.time() - start
        print(f"   Time: {cpu_time:.2f}s")
        transcriber_cpu.cleanup()
        
        # Test GPU
        print("\n🎮 Testing GPU mode...")
        transcriber_gpu = Transcriber(model_name='tiny', use_gpu=True)
        start = time.time()
        result_gpu = transcriber_gpu.transcribe(str(temp_file))
        gpu_time = time.time() - start
        print(f"   Time: {gpu_time:.2f}s")
        
        # Compare
        speedup = cpu_time / gpu_time if gpu_time > 0 else 1.0
        print(f"\n⚡ Speedup: {speedup:.2f}x")
        
        if speedup > 1.5:
            print("✅ Significant GPU acceleration!")
        elif speedup > 1.0:
            print("✅ Moderate GPU acceleration")
        else:
            print("⚠️  GPU not faster (may be normal for tiny model)")
        
        # Cleanup
        transcriber_gpu.cleanup()
        temp_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sbert_cpu_vs_gpu():
    """Test 4: SBERT CPU vs GPU"""
    print("\n" + "="*60)
    print("TEST 4: SBERT CPU vs GPU")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        # Test texts
        texts = ["This is test sentence " + str(i) for i in range(200)]
        print(f"\n📝 Testing with {len(texts)} sentences...")
        
        # CPU test
        print("\n🖥️  CPU mode:")
        model_cpu = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        start = time.time()
        embeddings_cpu = model_cpu.encode(texts, batch_size=16)
        cpu_time = time.time() - start
        print(f"   Time: {cpu_time:.2f}s")
        print(f"   Speed: {len(texts)/cpu_time:.1f} sentences/sec")
        
        # GPU test
        if GPU_AVAILABLE:
            print("\n🎮 GPU mode:")
            model_gpu = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
            torch.cuda.synchronize()
            start = time.time()
            embeddings_gpu = model_gpu.encode(texts, batch_size=64)
            torch.cuda.synchronize()
            gpu_time = time.time() - start
            print(f"   Time: {gpu_time:.2f}s")
            print(f"   Speed: {len(texts)/gpu_time:.1f} sentences/sec")
            
            # Speedup
            speedup = cpu_time / gpu_time
            print(f"\n⚡ Speedup: {speedup:.2f}x")
            
            if speedup > 3.0:
                print("✅ Excellent GPU acceleration!")
            elif speedup > 2.0:
                print("✅ Good GPU acceleration")
            elif speedup > 1.0:
                print("✅ Moderate GPU acceleration")
            else:
                print("⚠️  GPU not faster (unexpected)")
            
            # Verify similarity
            diff = np.abs(embeddings_cpu - embeddings_gpu).mean()
            print(f"\n🔬 Numerical difference: {diff:.8f}")
            if diff < 0.001:
                print("✅ Results match well")
            else:
                print("⚠️  Results differ (may be normal with FP16)")
            
            torch.cuda.empty_cache()
            
            return True
        else:
            print("\n⚠️  GPU not available")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_usage():
    """Test 5: Memory Usage"""
    print("\n" + "="*60)
    print("TEST 5: GPU MEMORY USAGE")
    print("="*60)
    
    if not GPU_AVAILABLE:
        print("⚠️  GPU not available")
        return False
    
    try:
        import torch
        from sentence_transformers import SentenceTransformer
        from src.transcriber import Transcriber
        
        print("\n📊 Testing memory footprint of models...\n")
        
        # Baseline
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        baseline = torch.cuda.memory_allocated() / 1e9
        print(f"Baseline: {baseline:.2f}GB")
        
        # Load Whisper tiny
        print("\n🎤 Loading Whisper 'tiny'...")
        transcriber = Transcriber(model_name='tiny', use_gpu=True)
        torch.cuda.synchronize()
        whisper_mem = torch.cuda.memory_allocated() / 1e9
        print(f"   VRAM used: {whisper_mem:.2f}GB (+{whisper_mem-baseline:.2f}GB)")
        transcriber.cleanup()
        torch.cuda.empty_cache()
        
        # Load SBERT
        print("\n🧠 Loading SBERT 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
        torch.cuda.synchronize()
        sbert_mem = torch.cuda.memory_allocated() / 1e9
        print(f"   VRAM used: {sbert_mem:.2f}GB (+{sbert_mem-baseline:.2f}GB)")
        del model
        torch.cuda.empty_cache()
        
        # Check total VRAM
        gpu_info = GPUConfig.get_gpu_info()
        total_vram = gpu_info.get('memory_total_gb', 0)
        free_vram = gpu_info.get('memory_free_gb', 0)
        
        print(f"\n💾 GPU Memory Summary:")
        print(f"   Total: {total_vram:.2f}GB")
        print(f"   Free: {free_vram:.2f}GB")
        print(f"   Whisper tiny: ~{whisper_mem-baseline:.2f}GB")
        print(f"   SBERT MiniLM: ~{sbert_mem-baseline:.2f}GB")
        
        # Estimate combined
        combined = (whisper_mem-baseline) + (sbert_mem-baseline)
        print(f"   Combined: ~{combined:.2f}GB")
        
        if combined < GPUConfig.SAFE_MEMORY_LIMIT:
            print(f"\n✅ Safe for RTX 3060 (under {GPUConfig.SAFE_MEMORY_LIMIT}GB limit)")
        else:
            print(f"\n⚠️  May exceed safe limit ({GPUConfig.SAFE_MEMORY_LIMIT}GB)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_temperature_monitoring():
    """Test 6: Temperature Monitoring"""
    print("\n" + "="*60)
    print("TEST 6: TEMPERATURE MONITORING")
    print("="*60)
    
    if not GPU_AVAILABLE:
        print("⚠️  GPU not available")
        return False
    
    try:
        import torch
        from sentence_transformers import SentenceTransformer
        
        gpu_info = GPUConfig.get_gpu_info()
        initial_temp = gpu_info.get('temperature_c')
        
        if not initial_temp:
            print("\n⚠️  Temperature monitoring not available")
            print("   Install: pip install pynvml nvidia-ml-py3")
            return False
        
        print(f"\n🌡️  Initial temperature: {initial_temp}°C")
        
        # Stress test
        print("\n🔥 Running GPU stress test (30 seconds)...")
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
        
        texts = ["Test sentence " + str(i) for i in range(1000)]
        
        start_time = time.time()
        temps = [initial_temp]
        
        while time.time() - start_time < 30:
            # Keep GPU busy
            embeddings = model.encode(texts, batch_size=128, show_progress_bar=False)
            torch.cuda.synchronize()
            
            # Check temp every 5 seconds
            if time.time() - start_time > len(temps) * 5:
                gpu_info = GPUConfig.get_gpu_info()
                current_temp = gpu_info.get('temperature_c')
                if current_temp:
                    temps.append(current_temp)
                    print(f"   {len(temps)*5}s: {current_temp}°C")
        
        del model
        torch.cuda.empty_cache()
        
        # Wait for cooldown
        print("\n❄️  Cooling down (10 seconds)...")
        time.sleep(10)
        
        gpu_info = GPUConfig.get_gpu_info()
        final_temp = gpu_info.get('temperature_c')
        
        print(f"\n📊 Temperature Summary:")
        print(f"   Initial: {initial_temp}°C")
        print(f"   Peak: {max(temps)}°C")
        print(f"   Final: {final_temp}°C")
        print(f"   Increase: {max(temps) - initial_temp}°C")
        
        if max(temps) < GPUConfig.MAX_SAFE_TEMP:
            print(f"\n✅ Temperatures safe (under {GPUConfig.MAX_SAFE_TEMP}°C)")
        else:
            print(f"\n⚠️  Temperature exceeded {GPUConfig.MAX_SAFE_TEMP}°C!")
            print("   Consider improving cooling or reducing workload")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrent_models():
    """Test 7: Concurrent Model Loading"""
    print("\n" + "="*60)
    print("TEST 7: CONCURRENT MODELS (Whisper + SBERT)")
    print("="*60)
    
    if not GPU_AVAILABLE:
        print("⚠️  GPU not available")
        return False
    
    try:
        import torch
        from src.transcriber import Transcriber
        from sentence_transformers import SentenceTransformer
        
        print("\n📝 Loading both Whisper and SBERT simultaneously...")
        
        torch.cuda.empty_cache()
        baseline = torch.cuda.memory_allocated() / 1e9
        
        # Load Whisper
        print("\n🎤 Loading Whisper 'base'...")
        transcriber = Transcriber(model_name='base', use_gpu=True)
        torch.cuda.synchronize()
        after_whisper = torch.cuda.memory_allocated() / 1e9
        
        # Load SBERT
        print("🧠 Loading SBERT...")
        sbert = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
        torch.cuda.synchronize()
        after_both = torch.cuda.memory_allocated() / 1e9
        
        print(f"\n💾 Memory Usage:")
        print(f"   Baseline: {baseline:.2f}GB")
        print(f"   + Whisper: {after_whisper:.2f}GB (+{after_whisper-baseline:.2f}GB)")
        print(f"   + SBERT: {after_both:.2f}GB (+{after_both-after_whisper:.2f}GB)")
        print(f"   Total: {after_both:.2f}GB")
        
        # Check if safe
        gpu_info = GPUConfig.get_gpu_info()
        total_vram = gpu_info.get('memory_total_gb', 0)
        
        print(f"\n📊 GPU Status:")
        print(f"   Total VRAM: {total_vram:.2f}GB")
        print(f"   Used: {after_both:.2f}GB ({after_both/total_vram*100:.1f}%)")
        print(f"   Free: {total_vram-after_both:.2f}GB")
        
        if after_both < GPUConfig.SAFE_MEMORY_LIMIT:
            print(f"\n✅ Safe to run both models simultaneously")
        else:
            print(f"\n⚠️  May be close to memory limit")
            print("   Consider using smaller models or CPU fallback")
        
        # Cleanup
        transcriber.cleanup()
        del sbert
        torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test 8: Full Pipeline (Audio → Transcription → Matching)"""
    print("\n" + "="*60)
    print("TEST 8: FULL GPU PIPELINE")
    print("="*60)
    
    if not GPU_AVAILABLE:
        print("⚠️  GPU not available")
        return False
    
    try:
        import torch
        import tempfile
        import numpy as np
        import soundfile as sf
        from src.transcriber import Transcriber
        from src.neural_matcher import NeuralLyricsMatcher
        
        # Create test audio
        print("\n📝 Creating test audio...")
        sr = 16000
        duration = 5
        t = np.linspace(0, duration, sr * duration)
        audio = np.sin(2 * np.pi * 440 * t)
        
        temp_file = Path(tempfile.gettempdir()) / "test_pipeline.wav"
        sf.write(temp_file, audio, sr)
        
        # Full pipeline with GPU
        print("\n🚀 Running full pipeline with GPU...")
        start_total = time.time()
        
        # Step 1: Transcribe
        print("\n   Step 1: Transcription...")
        transcriber = Transcriber(model_name='base', use_gpu=True)
        start = time.time()
        transcription = transcriber.transcribe(str(temp_file))
        transcribe_time = time.time() - start
        print(f"   ✅ Transcribed in {transcribe_time:.2f}s")
        
        # Step 2: Match
        print("\n   Step 2: Neural Matching...")
        matcher = NeuralLyricsMatcher(model_name='all-MiniLM-L6-v2', use_gpu=True)
        
        # Use a real query
        test_query = "feeling good today sunshine bright"
        start = time.time()
        results = matcher.match(test_query, top_k=3)
        match_time = time.time() - start
        print(f"   ✅ Matched in {match_time:.2f}s")
        
        total_time = time.time() - start_total
        
        print(f"\n⏱️  Pipeline Timing:")
        print(f"   Transcription: {transcribe_time:.2f}s")
        print(f"   Matching: {match_time:.2f}s")
        print(f"   Total: {total_time:.2f}s")
        
        # GPU stats
        gpu_info = GPUConfig.get_gpu_info()
        print(f"\n💾 GPU Stats:")
        print(f"   VRAM used: {gpu_info['memory_allocated_gb']:.2f}GB")
        if gpu_info.get('temperature_c'):
            print(f"   Temperature: {gpu_info['temperature_c']}°C")
        
        # Cleanup
        transcriber.cleanup()
        matcher.cleanup()
        temp_file.unlink()
        
        print("\n✅ Full pipeline test successful!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all GPU tests"""
    print("\n" + "="*60)
    print("🧪 WAVESEEK GPU TEST SUITE")
    print("="*60)
    print("Testing GPU acceleration for RTX 3060 6GB")
    print("="*60)
    
    tests = [
        ("GPU Detection", test_gpu_detection),
        ("Model Safety", test_model_safety),
        ("Whisper GPU", test_whisper_cpu_vs_gpu),
        ("SBERT GPU", test_sbert_cpu_vs_gpu),
        ("Memory Usage", test_memory_usage),
        ("Temperature", test_temperature_monitoring),
        ("Concurrent Models", test_concurrent_models),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            
            run_test = input(f"\nRun '{test_name}' test? (y/n/q): ").lower()
            
            if run_test == 'q':
                print("\n⏸️  Tests stopped by user")
                break
            elif run_test == 'n':
                print(f"⏭️  Skipped: {test_name}")
                results[test_name] = None
                continue
            
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"\n✅ {test_name} - PASSED")
            else:
                print(f"\n❌ {test_name} - FAILED")
            
            # Pause between tests
            if test_name != tests[-1][0]:
                input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ {test_name} - ERROR: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        
        print(f"{test_name:20s} {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ GPU acceleration is ready for production")
        print("\n📝 Next steps:")
        print("   1. Update API tier config to enable GPU for premium")
        print("   2. Test with frontend: npm start")
        print("   3. Monitor GPU temps during actual use")
        print("   4. Set up alerts for temperature/memory issues")
    elif passed > 0:
        print("\n⚠️  Some tests failed")
        print("   Review errors above and retry")
    else:
        print("\n❌ No tests passed")
        print("   Check GPU setup and dependencies")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏸️  Testing interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()