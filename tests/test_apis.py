"""
Test API endpoints (Spotify and YouTube)
Requires the API server to be running: python api.py
"""
import sys
from pathlib import Path
import requests
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable proxy for localhost
session = requests.Session()
session.trust_env = False

BASE_URL = "http://localhost:5000/api"


def test_spotify_api():
    """Test Spotify API endpoint"""
    print("🎵 Testing Spotify API...")
    print("-" * 60)
    
    try:
        response = session.post(
            f"{BASE_URL}/spotify/search",
            json={"artist": "Billie Eilish", "title": "bad guy"},
            timeout=15  # 15 second timeout
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"⚠️  Non-200 status code")
            print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except requests.Timeout:
        print("❌ Timeout - request took too long")
        return False
    except requests.ConnectionError:
        print("❌ Connection Error - Is the API server running?")
        print("💡 Start it with: python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_youtube_api():
    """Test YouTube API endpoint"""
    print("\n🎥 Testing YouTube API...")
    print("-" * 60)
    
    try:
        response = session.post(
            f"{BASE_URL}/youtube/search",
            json={"artist": "Billie Eilish", "title": "bad guy"},
            timeout=15  # 15 second timeout
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"⚠️  Non-200 status code")
            print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except requests.Timeout:
        print("❌ Timeout - YouTube API is taking too long")
        return False
    except requests.ConnectionError:
        print("❌ Connection Error - Is the API server running?")
        print("💡 Start it with: python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health_endpoint():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    print("-" * 60)
    
    try:
        response = session.get(f"{BASE_URL}/health", timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"⚠️  API returned non-200 status")
        
        return response.status_code == 200
        
    except requests.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Start it with: python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("🧪 API ENDPOINT TESTS")
    print("="*60 + "\n")
    
    print("⚠️  Make sure the API server is running: python api.py\n")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Spotify API", test_spotify_api),
        ("YouTube API", test_youtube_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s} - {status}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All API tests passed!")
    elif passed == 0:
        print("⚠️  API server may not be running")
        print("💡 Start it with: python api.py")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())