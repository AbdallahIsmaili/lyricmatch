import requests
import json
import os

# Disable proxy for localhost
session = requests.Session()
session.trust_env = False

BASE_URL = "http://localhost:5000/api"

# Test Spotify
print("🎵 Testing Spotify API...")
try:
    spotify_response = session.post(
        f"{BASE_URL}/spotify/search",
        json={"artist": "Billie Eilish", "title": "bad guy"},
        timeout=10  # 10 second timeout
    )
    print(f"Status: {spotify_response.status_code}")
    print(f"Response: {json.dumps(spotify_response.json(), indent=2)}\n")
except requests.Timeout:
    print("❌ Timeout - request took too long\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test YouTube
print("🎥 Testing YouTube API...")
try:
    youtube_response = session.post(
        f"{BASE_URL}/youtube/search",
        json={"artist": "Billie Eilish", "title": "bad guy"},
        timeout=10  # 10 second timeout
    )
    print(f"Status: {youtube_response.status_code}")
    print(f"Response: {json.dumps(youtube_response.json(), indent=2)}")
except requests.Timeout:
    print("❌ Timeout - YouTube API is taking too long")
except Exception as e:
    print(f"❌ Error: {e}")