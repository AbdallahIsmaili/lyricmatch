"""
Run all LyricMatch tests in sequence
"""
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_test(test_file, description):
    """
    Run a single test file
    
    Args:
        test_file: Path to test file
        description: Test description
    
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*70)
    print(f"Running: {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"\n❌ Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        return False


def main():
    """Run all tests"""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*20 + "LYRICMATCH TEST SUITE" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    
    tests_dir = Path(__file__).parent
    
    # Define tests in order
    tests = [
        {
            'file': tests_dir / 'test_setup.py',
            'name': 'Setup & Configuration Test',
            'required': True,
            'skip_if_fail': True
        },
        {
            'file': tests_dir / 'test_transcription.py',
            'name': 'Audio Transcription Test',
            'required': False,
            'skip_if_fail': False
        },
        {
            'file': tests_dir / 'test_compare_matchers.py',
            'name': 'Matcher Comparison Test',
            'required': False,
            'skip_if_fail': False
        },
        {
            'file': tests_dir / 'test_apis.py',
            'name': 'API Endpoints Test',
            'required': False,
            'skip_if_fail': False
        }
    ]
    
    results = []
    skipped = []
    
    for test in tests:
        if not test['file'].exists():
            print(f"\n⚠️  Test file not found: {test['file']}")
            results.append((test['name'], False))
            continue
        
        # Check if we should skip
        if results and test.get('skip_on_failure'):
            if not results[-1][1]:  # Previous test failed
                print(f"\n⏭️  Skipping {test['name']} (previous test failed)")
                skipped.append(test['name'])
                continue
        
        success = run_test(test['file'], test['name'])
        results.append((test['name'], success))
        
        # Stop if required test failed
        if test.get('required') and not success and test.get('skip_if_fail'):
            print(f"\n❌ Critical test failed. Stopping test suite.")
            break
    
    # Print summary
    print("\n\n" + "="*70)
    print("📊 TEST SUITE SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        required = " (REQUIRED)" if any(t['name'] == test_name and t.get('required') for t in tests) else ""
        print(f"{test_name:40s} - {status}{required}")
    
    if skipped:
        print(f"\n⏭️  Skipped Tests:")
        for test_name in skipped:
            print(f"   • {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    if skipped:
        print(f"Skipped: {len(skipped)} tests")
    print(f"{'='*70}\n")
    
    # Final message
    if passed == total:
        print("🎉 All tests passed! LyricMatch is fully functional.")
        print("\n📋 You can now:")
        print("   • Process audio files: python main.py <audio_file>")
        print("   • Start the API: python api.py")
        print("   • Run the web UI: python app.py")
        return 0
    else:
        failed_required = any(
            not success and any(t['name'] == name and t.get('required') for t in tests)
            for name, success in results
        )
        
        if failed_required:
            print("❌ Critical tests failed. Please fix these issues:")
            print("   1. Install missing packages: pip install -r requirements.txt")
            print("   2. Check system requirements")
            print("   3. Review error messages above")
        else:
            print("⚠️  Some optional tests failed, but core functionality works.")
            print("\n💡 Tips:")
            print("   • test_transcription: Add audio files to data/audio_samples/")
            print("   • test_compare_matchers: Run python setup_database.py")
            print("   • test_apis: Start API server with python api.py")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())