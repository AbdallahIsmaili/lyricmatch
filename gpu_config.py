"""
GPU Configuration and Safety Module for WaveSeek
Optimized for NVIDIA RTX 3060 6GB with thermal protection
Location: config/gpu_config.py
"""
import torch
import warnings
from pathlib import Path

class GPUConfig:
    """GPU configuration with safety limits for RTX 3060 6GB"""
    
    # GPU Availability
    CUDA_AVAILABLE = torch.cuda.is_available()
    DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"
    
    # RTX 3060 Specifications
    GPU_MEMORY_GB = 6.0
    SAFE_MEMORY_LIMIT = 5.0  # Leave 1GB headroom
    
    # Temperature Safety (°C)
    MAX_SAFE_TEMP = 80  # Conservative limit
    THROTTLE_TEMP = 75  # Start reducing workload
    
    # Whisper GPU Settings
    WHISPER_GPU_ENABLED = True
    WHISPER_FP16 = True  # Use FP16 for 2x speedup + 50% memory savings
    WHISPER_COMPUTE_TYPE = "float16"  # or "int8" for even more savings
    
    # Whisper Model Limits (Memory usage on RTX 3060 6GB)
    WHISPER_MODEL_LIMITS = {
        'tiny': {'vram_mb': 400, 'safe': True},      # ~390MB VRAM
        'base': {'vram_mb': 500, 'safe': True},      # ~500MB VRAM
        'small': {'vram_mb': 1200, 'safe': True},    # ~1.2GB VRAM
        'medium': {'vram_mb': 2800, 'safe': True},   # ~2.8GB VRAM
        'large': {'vram_mb': 5200, 'safe': False},   # ~5.2GB VRAM (risky!)
        'large-v2': {'vram_mb': 5200, 'safe': False},
        'large-v3': {'vram_mb': 5400, 'safe': False}
    }
    
    # SBERT GPU Settings
    SBERT_GPU_ENABLED = True
    SBERT_BATCH_SIZE_GPU = 64   # Optimal for RTX 3060
    SBERT_BATCH_SIZE_CPU = 16   # Fallback
    SBERT_FP16 = True           # Use half precision
    
    # SBERT Model Memory Usage
    SBERT_MODEL_LIMITS = {
        'all-MiniLM-L6-v2': {'vram_mb': 400, 'safe': True},      # Small, fast
        'all-mpnet-base-v2': {'vram_mb': 800, 'safe': True},     # Better quality
        'all-MiniLM-L12-v2': {'vram_mb': 500, 'safe': True},
        'paraphrase-MiniLM-L6-v2': {'vram_mb': 400, 'safe': True},
        'multi-qa-MiniLM-L6-cos-v1': {'vram_mb': 400, 'safe': True},
    }
    
    # Safety Monitoring
    MONITOR_GPU_TEMP = True
    MONITOR_GPU_MEMORY = True
    CHECK_INTERVAL_SECONDS = 5
    
    @classmethod
    def get_gpu_info(cls):
        """Get current GPU information"""
        if not cls.CUDA_AVAILABLE:
            return {
                'available': False,
                'message': 'No CUDA GPU detected'
            }
        
        try:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1e9
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / 1e9
            gpu_memory_reserved = torch.cuda.memory_reserved(0) / 1e9
            
            info = {
                'available': True,
                'name': gpu_name,
                'memory_total_gb': round(gpu_memory_total, 2),
                'memory_allocated_gb': round(gpu_memory_allocated, 2),
                'memory_reserved_gb': round(gpu_memory_reserved, 2),
                'memory_free_gb': round(gpu_memory_total - gpu_memory_reserved, 2),
                'device': cls.DEVICE,
                'cuda_version': torch.version.cuda,
                'pytorch_version': torch.__version__
            }
            
            # Try to get temperature (requires nvidia-ml-py3)
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                info['temperature_c'] = temp
                info['temp_safe'] = temp < cls.MAX_SAFE_TEMP
                pynvml.nvmlShutdown()
            except:
                info['temperature_c'] = None
                info['temp_safe'] = True
            
            return info
            
        except Exception as e:
            return {
                'available': True,
                'error': str(e),
                'message': 'GPU detected but error reading info'
            }
    
    @classmethod
    def check_model_safety(cls, model_type, model_name):
        """
        Check if model can safely run on GPU
        
        Args:
            model_type: 'whisper' or 'sbert'
            model_name: Model identifier
        
        Returns:
            dict with safety info
        """
        if model_type == 'whisper':
            limits = cls.WHISPER_MODEL_LIMITS.get(model_name, {'vram_mb': 999999, 'safe': False})
        elif model_type == 'sbert':
            limits = cls.SBERT_MODEL_LIMITS.get(model_name, {'vram_mb': 999999, 'safe': False})
        else:
            return {'safe': False, 'reason': 'Unknown model type'}
        
        gpu_info = cls.get_gpu_info()
        
        if not gpu_info['available']:
            return {'safe': False, 'reason': 'No GPU available', 'use_cpu': True}
        
        memory_needed_gb = limits['vram_mb'] / 1000
        memory_available_gb = gpu_info.get('memory_free_gb', 0)
        
        # Check memory
        if memory_needed_gb > cls.SAFE_MEMORY_LIMIT:
            return {
                'safe': False,
                'reason': f'Model needs {memory_needed_gb:.1f}GB, exceeds safe limit {cls.SAFE_MEMORY_LIMIT}GB',
                'use_cpu': True
            }
        
        if memory_needed_gb > memory_available_gb:
            return {
                'safe': False,
                'reason': f'Insufficient VRAM: need {memory_needed_gb:.1f}GB, have {memory_available_gb:.1f}GB',
                'use_cpu': True
            }
        
        # Check temperature
        temp = gpu_info.get('temperature_c')
        if temp and temp > cls.THROTTLE_TEMP:
            return {
                'safe': False,
                'reason': f'GPU too hot: {temp}°C (limit: {cls.THROTTLE_TEMP}°C)',
                'use_cpu': True
            }
        
        return {
            'safe': True,
            'memory_needed_gb': memory_needed_gb,
            'memory_available_gb': memory_available_gb,
            'use_gpu': True
        }
    
    @classmethod
    def optimize_for_model(cls, model_type, model_name):
        """Get optimal settings for specific model"""
        safety = cls.check_model_safety(model_type, model_name)
        
        if not safety.get('safe', False):
            return {
                'device': 'cpu',
                'batch_size': 16,
                'fp16': False,
                'reason': safety.get('reason', 'Safety check failed')
            }
        
        if model_type == 'whisper':
            return {
                'device': cls.DEVICE,
                'fp16': cls.WHISPER_FP16,
                'compute_type': cls.WHISPER_COMPUTE_TYPE,
                'reason': 'GPU acceleration enabled'
            }
        
        elif model_type == 'sbert':
            return {
                'device': cls.DEVICE,
                'batch_size': cls.SBERT_BATCH_SIZE_GPU,
                'fp16': cls.SBERT_FP16,
                'reason': 'GPU acceleration enabled'
            }
        
        return {'device': 'cpu', 'reason': 'Unknown model type'}
    
    @classmethod
    def clear_gpu_cache(cls):
        """Clear GPU cache to free memory"""
        if cls.CUDA_AVAILABLE:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    
    @classmethod
    def print_gpu_status(cls):
        """Print formatted GPU status"""
        info = cls.get_gpu_info()
        
        if not info['available']:
            print("\n🚫 GPU Status: NOT AVAILABLE")
            print(f"   {info.get('message', 'No GPU detected')}")
            return
        
        print("\n🎮 GPU Status")
        print("="*60)
        print(f"  Device: {info.get('name', 'Unknown')}")
        print(f"  CUDA: {info.get('cuda_version', 'Unknown')}")
        print(f"  PyTorch: {info.get('pytorch_version', 'Unknown')}")
        print(f"\n💾 Memory:")
        print(f"  Total:     {info['memory_total_gb']:.2f} GB")
        print(f"  Free:      {info['memory_free_gb']:.2f} GB")
        print(f"  Allocated: {info['memory_allocated_gb']:.2f} GB")
        
        if info.get('temperature_c'):
            temp = info['temperature_c']
            temp_status = "✅ OK" if temp < cls.THROTTLE_TEMP else "⚠️ HIGH"
            print(f"\n🌡️  Temperature: {temp}°C {temp_status}")
        
        print("="*60)


# Auto-detect and warn on import
if GPUConfig.CUDA_AVAILABLE:
    gpu_info = GPUConfig.get_gpu_info()
    print(f"✅ GPU Detected: {gpu_info.get('name', 'Unknown')}")
    print(f"   VRAM: {gpu_info.get('memory_free_gb', 0):.1f}GB free / {gpu_info.get('memory_total_gb', 0):.1f}GB total")
    
    if gpu_info.get('temperature_c'):
        print(f"   Temp: {gpu_info['temperature_c']}°C")
else:
    print("⚠️  No GPU detected - using CPU mode")
    warnings.warn("CUDA not available. Install CUDA toolkit for GPU acceleration.")


if __name__ == "__main__":
    GPUConfig.print_gpu_status()
    
    print("\n🔍 Model Safety Checks:")
    print("="*60)
    
    # Test Whisper models
    print("\n🎤 Whisper Models:")
    for model in ['tiny', 'base', 'small', 'medium', 'large']:
        safety = GPUConfig.check_model_safety('whisper', model)
        status = "✅ SAFE" if safety['safe'] else "❌ UNSAFE"
        print(f"  {model:10s} - {status:10s} {safety.get('reason', '')}")
    
    # Test SBERT models
    print("\n🧠 SBERT Models:")
    for model in ['all-MiniLM-L6-v2', 'all-mpnet-base-v2']:
        safety = GPUConfig.check_model_safety('sbert', model)
        status = "✅ SAFE" if safety['safe'] else "❌ UNSAFE"
        print(f"  {model:30s} - {status}")