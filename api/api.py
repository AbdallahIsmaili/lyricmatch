"""
Flask API Backend for LyricMatch Web App with Tier System
Location: api/api.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import tempfile
import time
from threading import Thread
import uuid
import sys
import numpy as np
import math

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can use them
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Add parent directory to path to import from root
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config import Config
from src.audio_processor import AudioProcessor
from src.transcriber import Transcriber
from src.matcher import LyricsMatcher
from src.neural_matcher import NeuralLyricsMatcher

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'lyricmatch_uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}  

# Global state for processing jobs
processing_jobs = {}

# Tier configurations
TIER_CONFIGS = {
    'free': {
        'name': 'Free',
        'whisper_models': ['tiny', 'base'],
        'matching_engines': ['tfidf'],
        'sbert_models': [],
        'max_file_size': 20 * 1024 * 1024,  # 10MB
        'daily_limit': 5,
        'features': ['Basic TF-IDF matching', 'Fast processing', 'Up to 5 searches/day']
    },
    'premium': {
        'name': 'Premium',
        'whisper_models': ['tiny', 'base', 'small', 'medium', 'large'],
        'matching_engines': ['tfidf', 'neural', 'hybrid'],
        'sbert_models': ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'paraphrase-MiniLM-L6-v2'],
        'max_file_size': 200 * 1024 * 1024,  # 50MB
        'daily_limit': None,  # Unlimited
        'features': [
            'Advanced Neural Embeddings (BERT)',
            'Hybrid matching algorithms',
            'All Whisper models (tiny to large)',
            'Unlimited searches',
            'Priority processing',
            'Higher accuracy'
        ]
    }
}

def convert_to_native_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif obj is None or isinstance(obj, (str, int, float, bool)):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj
    else:
        return str(obj)

class LyricMatchAPI:
    """API wrapper for LyricMatch with tier support"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.transcribers = {}  # Cache transcribers by model
        self.matchers = {}  # Cache matchers by engine
        print("✅ LyricMatch API initialized")
    
    def get_transcriber(self, model_name):
        """Get or create transcriber for model"""
        if model_name not in self.transcribers:
            print(f"🔄 Loading Whisper model: {model_name}")
            self.transcribers[model_name] = Transcriber(model_name=model_name)
        return self.transcribers[model_name]
    
    def get_matcher(self, engine, sbert_model=None):
        """Get or create matcher for engine"""
        cache_key = f"{engine}_{sbert_model or 'default'}"
        
        if cache_key not in self.matchers:
            print(f"🔄 Loading {engine.upper()} matcher")
            if engine == 'tfidf':
                self.matchers[cache_key] = LyricsMatcher()
            elif engine in ['neural', 'hybrid']:
                model = sbert_model or Config.SBERT_MODEL
                self.matchers[cache_key] = NeuralLyricsMatcher(model_name=model)
            else:
                raise ValueError(f"Unknown engine: {engine}")
        
        return self.matchers[cache_key]
    
    def process_audio(self, job_id, audio_path, config):
        """Process audio file with tier-specific configuration"""
        try:
            print(f"\n🔄 Starting processing for job {job_id}")
            print(f"⚙️ Tier: {config['tier']}")
            print(f"⚙️ Whisper: {config['whisper_model']}")
            print(f"⚙️ Engine: {config['engine']}")
            
            # Update status: preprocessing
            processing_jobs[job_id]['status'] = 'preprocessing'
            processing_jobs[job_id]['progress'] = 10
            processing_jobs[job_id]['tier'] = config['tier']
            
            audio, sr = self.audio_processor.preprocess_audio(audio_path)
            
            # Update status: transcribing
            processing_jobs[job_id]['status'] = 'transcribing'
            processing_jobs[job_id]['progress'] = 30
            
            transcriber = self.get_transcriber(config['whisper_model'])
            transcription = transcriber.transcribe(str(audio_path))
            
            # Update status: matching
            processing_jobs[job_id]['status'] = 'matching'
            processing_jobs[job_id]['progress'] = 70
            processing_jobs[job_id]['transcription'] = transcription['text']
            processing_jobs[job_id]['language'] = transcription['language']
            
            matcher = self.get_matcher(config['engine'], config.get('sbert_model'))
            results = matcher.match_with_details(transcription['text'], top_k=5)
            
            print(f"🎵 Found {len(results)} match(es)")
            
            # Convert and validate results
            results_native = convert_to_native_types(results)
            if not isinstance(results_native, list):
                results_native = []
            
            cleaned_results = []
            for result in results_native:
                if isinstance(result, dict):
                    cleaned_result = {}
                    for key, value in result.items():
                        if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
                            cleaned_result[key] = None
                        else:
                            cleaned_result[key] = value
                    cleaned_results.append(cleaned_result)
            
            # Update status: complete
            processing_jobs[job_id]['status'] = 'complete'
            processing_jobs[job_id]['progress'] = 100
            processing_jobs[job_id]['results'] = cleaned_results
            processing_jobs[job_id]['audio_info'] = {
                'duration': float(transcription['duration']) if not math.isnan(transcription['duration']) else None,
                'sample_rate': int(sr)
            }
            processing_jobs[job_id]['config_used'] = {
                'whisper_model': config['whisper_model'],
                'engine': config['engine'],
                'sbert_model': config.get('sbert_model')
            }
            
            print(f"✅ Job {job_id} completed successfully")
            
            # Cleanup
            try:
                os.remove(audio_path)
            except Exception as cleanup_error:
                print(f"⚠️ Could not remove temp file: {cleanup_error}")
            
        except Exception as e:
            processing_jobs[job_id]['status'] = 'error'
            processing_jobs[job_id]['error'] = str(e)
            processing_jobs[job_id]['progress'] = 0
            print(f"❌ Error processing {job_id}: {e}")
            import traceback
            traceback.print_exc()

# Initialize API
lyricmatch_api = LyricMatchAPI()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'database_songs': len(lyricmatch_api.matchers.get('tfidf_default', LyricsMatcher()).songs_df) if lyricmatch_api.matchers.get('tfidf_default') else 0
    })

@app.route('/api/tiers', methods=['GET'])
def get_tiers():
    """Get available tiers and their features"""
    return jsonify({
        'tiers': TIER_CONFIGS
    })


@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """Upload audio file with tier configuration"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get tier and configuration
    tier = request.form.get('tier', 'free')
    whisper_model = request.form.get('whisper_model', 'tiny')
    engine = request.form.get('engine', 'tfidf')
    sbert_model = request.form.get('sbert_model', None)
    
    # Validate tier
    if tier not in TIER_CONFIGS:
        return jsonify({'error': 'Invalid tier'}), 400
    
    tier_config = TIER_CONFIGS[tier]
    
    # Validate configuration against tier
    if whisper_model not in tier_config['whisper_models']:
        return jsonify({'error': f'Whisper model {whisper_model} not available in {tier} tier'}), 403
    
    if engine not in tier_config['matching_engines']:
        return jsonify({'error': f'Matching engine {engine} not available in {tier} tier'}), 403
    
    if sbert_model and sbert_model not in tier_config.get('sbert_models', []):
        return jsonify({'error': f'SBERT model {sbert_model} not available in {tier} tier'}), 403
    
    # Check file size
    content_length = request.content_length
    if content_length and content_length > tier_config['max_file_size']:
        return jsonify({
            'error': f'File size exceeds {tier_config["max_file_size"] / (1024*1024):.1f}MB limit for {tier} tier'
        }), 413

    # Fallback: check actual file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0, os.SEEK_SET)

    if file_size > tier_config['max_file_size']:
        return jsonify({
            'error': f'File size exceeds {tier_config["max_file_size"] / (1024*1024):.1f}MB limit for {tier} tier'
        }), 413
    
    # Check file extension - support both explicit extensions and content type
    file_ext = Path(file.filename).suffix.lower()
    
    # Handle browser recordings that might not have proper extension
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        # Check content type for webm
        if file.content_type and 'webm' in file.content_type:
            file_ext = '.webm'
        elif file.content_type and 'audio' in file.content_type:
            # Accept generic audio types
            file_ext = '.webm'  # Default to webm for browser recordings
        else:
            return jsonify({'error': f'Unsupported format: {file_ext or file.content_type}'}), 400
    
    # Save file
    job_id = str(uuid.uuid4())
    filename = secure_filename(f"{job_id}{file_ext}")
    filepath = UPLOAD_FOLDER / filename
    file.save(str(filepath))
    
    print(f"\n📤 New upload: {file.filename}")
    print(f"🆔 Job ID: {job_id}")
    print(f"🎯 Tier: {tier}")
    print(f"📁 Format: {file_ext}")
    
    # Convert WebM to WAV for processing
    if file_ext == '.webm':
        try:
            from pydub import AudioSegment
            
            print(f"🔄 Converting WebM to WAV...")
            audio = AudioSegment.from_file(str(filepath), format="webm")
            new_filepath = filepath.with_suffix('.wav')
            audio.export(str(new_filepath), format="wav")
            
            # Remove original webm
            os.remove(str(filepath))
            filepath = new_filepath
            
            print(f"✅ Converted WebM to WAV: {new_filepath.name}")
        except Exception as e:
            print(f"⚠️ WebM conversion failed: {e}")
            # Clean up and return error
            try:
                os.remove(str(filepath))
            except:
                pass
            return jsonify({'error': f'Failed to process WebM audio: {str(e)}'}), 500
    
    # Initialize job
    processing_jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'filename': file.filename,
        'created_at': time.time(),
        'tier': tier
    }
    
    # Processing configuration
    config = {
        'tier': tier,
        'whisper_model': whisper_model,
        'engine': engine,
        'sbert_model': sbert_model
    }
    
    # Start processing
    thread = Thread(
        target=lyricmatch_api.process_audio,
        args=(job_id, filepath, config)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': 'Processing started',
        'tier': tier
    })


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status"""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    
    progress = job.get('progress', 0)
    if not isinstance(progress, int):
        progress = int(progress) if progress else 0
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': progress,
        'filename': job['filename'],
        'tier': job.get('tier', 'free')
    }
    
    if 'transcription' in job:
        response['transcription'] = job['transcription']
        response['language'] = job['language']
    
    if 'results' in job:
        response['results'] = job['results']
        response['audio_info'] = job['audio_info']
        response['config_used'] = job.get('config_used', {})
    
    if 'error' in job:
        response['error'] = job['error']
    
    return jsonify(response)

@app.route('/api/search', methods=['POST'])
def search_lyrics():
    """Search by text query"""
    data = request.json
    query = data.get('query', '')
    tier = data.get('tier', 'free')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    matcher = lyricmatch_api.get_matcher('tfidf')
    results = matcher.match_with_details(query, top_k=5)
    results_native = convert_to_native_types(results)
    
    return jsonify({
        'results': results_native,
        'query': query,
        'tier': tier
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        matcher = lyricmatch_api.get_matcher('tfidf')
        stats = matcher.db.get_database_stats()
        stats_native = convert_to_native_types(stats)
        return jsonify(stats_native)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spotify/search', methods=['POST'])
def search_spotify():
    """Get direct Spotify track URL"""
    data = request.json
    artist = data.get('artist', '')
    title = data.get('title', '')
    
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        # You'll need to set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in environment
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        query = f"track:{title} artist:{artist}"
        results = sp.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return jsonify({
                'url': track['external_urls']['spotify'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track['preview_url']
            })
    except Exception as e:
        print(f"Spotify API error: {e}")
    
    return jsonify({'url': None, 'image': None}), 404

@app.route('/api/youtube/search', methods=['POST'])
def search_youtube():
    """Get direct YouTube video URL"""
    data = request.json
    artist = data.get('artist', '')
    title = data.get('title', '')
    
    print(f"🔍 YouTube search: {artist} - {title}")
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not api_key:
            print("❌ Missing YouTube API key")
            return jsonify({'url': None, 'error': 'Missing API key'}), 500
        
        print(f"✅ YouTube API key found: {api_key[:10]}...")
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        print(f"🔄 Making YouTube API request...")
        search_response = youtube.search().list(
            q=f"{artist} {title} official",
            part='id,snippet',
            maxResults=1,
            type='video'
        ).execute()
        
        print(f"✅ YouTube API response received")
        
        if search_response.get('items'):
            video_id = search_response['items'][0]['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail = search_response['items'][0]['snippet']['thumbnails']['high']['url']
            
            print(f"✅ Found YouTube video: {video_url}")
            
            return jsonify({
                'url': video_url,
                'thumbnail': thumbnail
            })
        else:
            print(f"❌ No YouTube results found")
            return jsonify({'url': None}), 404
            
    except HttpError as e:
        print(f"❌ YouTube API HTTP error: {e}")
        return jsonify({'url': None, 'error': str(e)}), 500
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'url': None, 'error': str(e)}), 500
    

# Clean up old jobs periodically
def cleanup_old_jobs():
    """Remove jobs older than 1 hour"""
    current_time = time.time()
    jobs_to_remove = []
    
    for job_id, job in processing_jobs.items():
        if current_time - job['created_at'] > 3600:
            jobs_to_remove.append(job_id)
    
    for job_id in jobs_to_remove:
        del processing_jobs[job_id]
    
    if jobs_to_remove:
        print(f"🧹 Cleaned up {len(jobs_to_remove)} old job(s)")

def schedule_cleanup():
    while True:
        time.sleep(1800)
        cleanup_old_jobs()

cleanup_thread = Thread(target=schedule_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting LyricMatch SaaS API Server")
    print("="*60)
    print(f"🌐 Running on: http://localhost:5000")
    print(f"🔗 Health Check: http://localhost:5000/api/health")
    print(f"🎯 Tiers Endpoint: http://localhost:5000/api/tiers")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)