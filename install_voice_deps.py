"""
Install Voice Analyzer Dependencies
Ensures all required packages are installed
"""
import subprocess
import sys


def install_package(package):
    """Install a package using pip"""
    print(f"\n📦 Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False


def check_package(package):
    """Check if a package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║           VOICE ANALYZER - DEPENDENCY INSTALLER                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Required packages
    required = {
        'librosa': 'librosa',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'sklearn': 'scikit-learn',
        'torch': 'torch'
    }
    
    # Optional packages
    optional = {
        'pyannote.audio': 'pyannote-audio'
    }
    
    print("\n🔍 Checking required dependencies...\n")
    
    missing = []
    installed = []
    
    for import_name, package_name in required.items():
        if check_package(import_name):
            print(f"✅ {package_name} - already installed")
            installed.append(package_name)
        else:
            print(f"❌ {package_name} - missing")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Found {len(missing)} missing package(s)")
        print("\n📦 Installing missing packages...\n")
        
        for package in missing:
            install_package(package)
    else:
        print("\n✅ All required packages already installed!")
    
    # Check optional
    print("\n\n🔍 Checking optional dependencies...\n")
    
    for import_name, package_name in optional.items():
        if check_package(import_name):
            print(f"✅ {package_name} - installed")
        else:
            print(f"⚠️  {package_name} - not installed (optional)")
            print(f"   Install with: pip install {package_name}")
    
    # Verify installation
    print("\n\n🧪 Verifying installation...\n")
    
    try:
        import librosa
        print(f"✅ librosa version: {librosa.__version__}")
    except ImportError:
        print("❌ librosa import failed")
    
    try:
        import numpy
        print(f"✅ numpy version: {numpy.__version__}")
    except ImportError:
        print("❌ numpy import failed")
    
    try:
        import scipy
        print(f"✅ scipy version: {scipy.__version__}")
    except ImportError:
        print("❌ scipy import failed")
    
    try:
        import sklearn
        print(f"✅ scikit-learn version: {sklearn.__version__}")
    except ImportError:
        print("❌ scikit-learn import failed")
    
    try:
        import torch
        print(f"✅ torch version: {torch.__version__}")
    except ImportError:
        print("❌ torch import failed")
    
    print("\n\n" + "="*70)
    print("  INSTALLATION COMPLETE")
    print("="*70)
    
    print("\n💡 Next steps:")
    print("   1. Test voice analyzer: python tests/test_voice_analyzer.py")
    print("   2. If issues persist, try: pip install --upgrade librosa scipy")
    print("   3. For GPU support: python setup_gpu_windows.py")
    print("\n")


if __name__ == "__main__":
    main()