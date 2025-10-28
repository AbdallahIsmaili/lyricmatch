"""
Flask API Backend for WaveSeek Web App with Tier System
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

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.lyrics_fetcher import LyricsFetcher

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


try:
    from gpu_config import GPUConfig
    GPU_AVAILABLE = GPUConfig.CUDA_AVAILABLE
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  GPU config not available")


# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'waveseek_uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}  

# Global state for processing jobs
processing_jobs = {}

TIER_CONFIGS = {
    'free': {
        'name': 'Free',
        'whisper_models': ['tiny', 'base'],
        'matching_engines': ['tfidf'],
        'sbert_models': [],
        'max_file_size': 20 * 1024 * 1024,  # 20MB
        'max_duration_seconds': 30,  # 30 seconds
        'daily_limit': 5,
        'gpu_enabled': False,  # NEW
        'features': [
            'Basic TF-IDF matching',
            'CPU processing',
            'Up to 30s audio',
            '5 searches/day'
        ]
    },
    'premium': {
        'name': 'Premium',
        'whisper_models': ['tiny', 'base', 'small', 'medium', 'large'],
        'matching_engines': ['tfidf', 'neural', 'hybrid'],
        'sbert_models': ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'paraphrase-MiniLM-L6-v2'],
        'max_file_size': 200 * 1024 * 1024,  # 200MB
        'max_duration_seconds': 180,  # 3 minutes
        'daily_limit': None,  # Unlimited
        'gpu_enabled': GPU_AVAILABLE,  # NEW - Enable GPU if available
        'features': [
            '🎮 GPU Acceleration (RTX 3060)',
            '🧠 Advanced Neural Embeddings',
            '⚡ 5-10x Faster Processing',
            'All Whisper models',
            'Up to 2min audio',
            'Unlimited searches',
            'Priority queue'
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


class WaveSeekAPI:
    """API wrapper with GPU support"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.transcribers = {}
        self.matchers = {}
        
        # Show GPU status on startup
        if GPU_AVAILABLE:
            print("\n" + "="*60)
            GPUConfig.print_gpu_status()
            print("="*60 + "\n")
        else:
            print("⚠️  GPU not available - CPU mode only")
        
        print("✅ WaveSeek API initialized")
    
    def get_transcriber(self, model_name, use_gpu=False):
        """Get or create transcriber with GPU option"""
        cache_key = f"{model_name}_{'gpu' if use_gpu else 'cpu'}"
        
        if cache_key not in self.transcribers:
            print(f"📄 Loading Whisper: {model_name} ({'GPU' if use_gpu else 'CPU'})")
            self.transcribers[cache_key] = Transcriber(
                model_name=model_name,
                use_gpu=use_gpu,
                force_cpu=not use_gpu
            )
        return self.transcribers[cache_key]
    
    def get_matcher(self, engine, sbert_model=None, use_gpu=False):
        """Get or create matcher with GPU option"""
        cache_key = f"{engine}_{sbert_model or 'default'}_{'gpu' if use_gpu else 'cpu'}"
        
        if cache_key not in self.matchers:
            print(f"📊 Loading {engine.upper()} matcher ({'GPU' if use_gpu else 'CPU'})")
            if engine == 'tfidf':
                self.matchers[cache_key] = LyricsMatcher()
            elif engine in ['neural', 'hybrid']:
                model = sbert_model or Config.SBERT_MODEL
                self.matchers[cache_key] = NeuralLyricsMatcher(
                    model_name=model,
                    use_gpu=use_gpu,
                    force_cpu=not use_gpu
                )
            else:
                raise ValueError(f"Unknown engine: {engine}")
        
        return self.matchers[cache_key]
    
    def process_audio(self, job_id, audio_path, config):
        """Process audio with GPU support"""
        try:
            tier = config['tier']
            use_gpu = config.get('use_gpu', False)
            
            print(f"\n📄 Processing job {job_id}")
            print(f"⚙️  Tier: {tier}")
            print(f"⚙️  GPU: {'Enabled' if use_gpu else 'Disabled'}")
            print(f"⚙️  Whisper: {config['whisper_model']}")
            print(f"⚙️  Engine: {config['engine']}")
            
            # Update status
            processing_jobs[job_id]['status'] = 'preprocessing'
            processing_jobs[job_id]['progress'] = 10
            processing_jobs[job_id]['tier'] = tier
            processing_jobs[job_id]['gpu_enabled'] = use_gpu
            
            # Preprocess
            audio, sr = self.audio_processor.preprocess_audio(audio_path)
            audio_info = self.audio_processor.get_audio_info(str(audio_path))
            
            # Validate duration for tier
            duration = audio_info.get('duration', 0)
            max_duration = TIER_CONFIGS[tier]['max_duration_seconds']
            
            if duration > max_duration:
                raise Exception(
                    f"Audio too long: {duration:.1f}s (max {max_duration}s for {tier} tier)"
                )
            
            # Transcribe
            processing_jobs[job_id]['status'] = 'transcribing'
            processing_jobs[job_id]['progress'] = 30
            
            transcriber = self.get_transcriber(config['whisper_model'], use_gpu)
            transcription = transcriber.transcribe(str(audio_path))
            
            # Match
            processing_jobs[job_id]['status'] = 'matching'
            processing_jobs[job_id]['progress'] = 70
            processing_jobs[job_id]['transcription'] = transcription['text']
            processing_jobs[job_id]['language'] = transcription['language']
            
            matcher = self.get_matcher(config['engine'], config.get('sbert_model'), use_gpu)
            results = matcher.match_with_details(transcription['text'], top_k=5)
            
            # Convert results
            results_native = convert_to_native_types(results)
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
            
            # Complete
            processing_jobs[job_id]['status'] = 'complete'
            processing_jobs[job_id]['progress'] = 100
            processing_jobs[job_id]['results'] = cleaned_results
            processing_jobs[job_id]['audio_info'] = {
                'duration': float(transcription['duration']) if not math.isnan(transcription['duration']) else None,
                'sample_rate': int(sr),
                'channels': audio_info.get('channels', 1),
                'bitrate': audio_info.get('bitrate', 0),
                'file_size_mb': audio_info.get('file_size_mb', 0),
                'processing_time': transcription.get('processing_time', 0)
            }
            processing_jobs[job_id]['config_used'] = {
                'whisper_model': config['whisper_model'],
                'engine': config['engine'],
                'sbert_model': config.get('sbert_model'),
                'gpu_enabled': use_gpu,
                'device_used': transcription.get('device_used', 'cpu')
            }
            
            # GPU performance stats
            if use_gpu and GPU_AVAILABLE:
                gpu_info = GPUConfig.get_gpu_info()
                processing_jobs[job_id]['gpu_stats'] = {
                    'vram_used_gb': gpu_info.get('memory_allocated_gb', 0),
                    'temperature_c': gpu_info.get('temperature_c'),
                    'speedup': transcription.get('speedup_factor', 1.0)
                }
            
            print(f"✅ Job {job_id} complete")
            
            # Cleanup
            try:
                os.remove(audio_path)
            except:
                pass
            
        except Exception as e:
            processing_jobs[job_id]['status'] = 'error'
            processing_jobs[job_id]['error'] = str(e)
            processing_jobs[job_id]['progress'] = 0
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


# Initialize API
waveseek_api = WaveSeekAPI()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'database_songs': len(waveseek_api.matchers.get('tfidf_default', LyricsMatcher()).songs_df) if waveseek_api.matchers.get('tfidf_default') else 0
    })

@app.route('/api/tiers', methods=['GET'])
def get_tiers():
    """Get available tiers and their features"""
    return jsonify({
        'tiers': TIER_CONFIGS
    })


@app.route('/api/gpu/status', methods=['GET'])
def gpu_status():
    """Get current GPU status"""
    if not GPU_AVAILABLE:
        return jsonify({
            'available': False,
            'message': 'GPU not available on this server'
        })
    
    gpu_info = GPUConfig.get_gpu_info()
    
    # Check if safe for premium tier
    safe_for_whisper = GPUConfig.check_model_safety('whisper', 'medium')
    safe_for_sbert = GPUConfig.check_model_safety('sbert', 'all-MiniLM-L6-v2')
    
    return jsonify({
        'available': True,
        'name': gpu_info.get('name', 'Unknown'),
        'memory_total_gb': gpu_info.get('memory_total_gb', 0),
        'memory_free_gb': gpu_info.get('memory_free_gb', 0),
        'memory_used_gb': gpu_info.get('memory_allocated_gb', 0),
        'temperature_c': gpu_info.get('temperature_c'),
        'temp_safe': gpu_info.get('temp_safe', True),
        'cuda_version': gpu_info.get('cuda_version'),
        'whisper_safe': safe_for_whisper.get('safe', False),
        'sbert_safe': safe_for_sbert.get('safe', False),
        'recommended_models': {
            'whisper': ['tiny', 'base', 'small', 'medium'],
            'sbert': ['all-MiniLM-L6-v2', 'all-mpnet-base-v2']
        }
    })


@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """Upload with GPU support"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get config
    tier = request.form.get('tier', 'free')
    whisper_model = request.form.get('whisper_model', 'tiny')
    engine = request.form.get('engine', 'tfidf')
    sbert_model = request.form.get('sbert_model', None)
    use_gpu = request.form.get('use_gpu', 'false').lower() == 'true'
    
    # Validate tier
    if tier not in TIER_CONFIGS:
        return jsonify({'error': 'Invalid tier'}), 400
    
    tier_config = TIER_CONFIGS[tier]
    
    # GPU check
    if use_gpu and not tier_config['gpu_enabled']:
        return jsonify({
            'error': f'GPU acceleration not available in {tier} tier',
            'upgrade_message': 'Upgrade to Premium for GPU acceleration'
        }), 403
    
    if use_gpu and not GPU_AVAILABLE:
        return jsonify({
            'error': 'GPU not available on server',
            'fallback': 'Processing with CPU'
        }), 503
    
    # Validate models
    if whisper_model not in tier_config['whisper_models']:
        return jsonify({
            'error': f'Whisper {whisper_model} not in {tier} tier'
        }), 403
    
    if engine not in tier_config['matching_engines']:
        return jsonify({
            'error': f'Engine {engine} not in {tier} tier'
        }), 403
    
    # File size check
    content_length = request.content_length
    if content_length and content_length > tier_config['max_file_size']:
        return jsonify({
            'error': f'File too large for {tier} tier',
            'max_size_mb': tier_config['max_file_size'] / (1024*1024)
        }), 413
    
    # Save file
    file_ext = Path(file.filename).suffix.lower()
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        if file.content_type and 'webm' in file.content_type:
            file_ext = '.webm'
        else:
            return jsonify({'error': f'Unsupported format: {file_ext}'}), 400
    
    job_id = str(uuid.uuid4())
    filename = secure_filename(f"{job_id}{file_ext}")
    filepath = UPLOAD_FOLDER / filename
    file.save(str(filepath))
    
    print(f"\n📤 Upload: {file.filename}")
    print(f"🆔 Job: {job_id}")
    print(f"🎯 Tier: {tier}")
    print(f"🎮 GPU: {'Enabled' if use_gpu else 'Disabled'}")
    
    # Convert WebM
    if file_ext == '.webm':
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(filepath), format="webm")
            new_filepath = filepath.with_suffix('.wav')
            audio.export(str(new_filepath), format="wav")
            os.remove(str(filepath))
            filepath = new_filepath
        except Exception as e:
            try:
                os.remove(str(filepath))
            except:
                pass
            return jsonify({'error': f'WebM conversion failed: {str(e)}'}), 500
    
    # Initialize job
    processing_jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'filename': file.filename,
        'created_at': time.time(),
        'tier': tier,
        'gpu_enabled': use_gpu
    }
    
    # Config
    config = {
        'tier': tier,
        'whisper_model': whisper_model,
        'engine': engine,
        'sbert_model': sbert_model,
        'use_gpu': use_gpu
    }
    
    # Start processing
    thread = Thread(
        target=waveseek_api.process_audio,
        args=(job_id, filepath, config)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': 'Processing started',
        'tier': tier,
        'gpu_enabled': use_gpu
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
    
    matcher = waveseek_api.get_matcher('tfidf')
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
        matcher = waveseek_api.get_matcher('tfidf')
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
    


@app.route('/api/lyrics/fetch-artist', methods=['POST'])
def fetch_artist_lyrics():
    """Fetch and add artist's songs to database with automatic index rebuild"""
    data = request.json
    artist_name = data.get('artist_name', '')
    max_songs = data.get('max_songs', 50)  # Allow customization
    
    if not artist_name:
        return jsonify({'error': 'Artist name required'}), 400
    
    try:
        print(f"\n{'='*60}")
        print(f"🎵 Fetching lyrics for: {artist_name}")
        print(f"{'='*60}")
        
        fetcher = LyricsFetcher()
        songs = fetcher.fetch_artist_complete(artist_name, max_songs=max_songs)
        
        print(f"\n{'='*60}")
        print(f"🔄 Clearing cached matchers and rebuilding indexes...")
        print(f"{'='*60}")
        
        # Clear all cached matchers to force reload with new data
        waveseek_api.matchers.clear()
        
        # Force rebuild of indexes
        print("📊 Rebuilding TF-IDF index...")
        tfidf_matcher = waveseek_api.get_matcher('tfidf')
        print(f"   ✅ TF-IDF ready with {len(tfidf_matcher.songs_df)} songs")
        
        print("🧠 Rebuilding neural embeddings...")
        neural_matcher = waveseek_api.get_matcher('neural')
        neural_matcher.rebuild_embeddings()
        print(f"   ✅ Neural embeddings ready with {len(neural_matcher.songs_df)} songs")
        
        print(f"\n{'='*60}")
        print(f"✅ ALL DONE! {artist_name} songs are now searchable!")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'artist': artist_name,
            'songs_added': len(songs),
            'total_songs_in_db': len(tfidf_matcher.songs_df),
            'message': f'Added {len(songs)} songs for {artist_name}. All indexes rebuilt.',
            'indexes_rebuilt': True
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error: {error_details}")
        
        return jsonify({
            'error': str(e),
            'details': error_details
        }), 500


@app.route('/api/lyrics/rebuild-indexes', methods=['POST'])
def rebuild_indexes():
    """Manually rebuild all search indexes (useful after manual database changes)"""
    try:
        print(f"\n{'='*60}")
        print(f"🔄 Manual index rebuild requested")
        print(f"{'='*60}")
        
        # Clear cache
        waveseek_api.matchers.clear()
        
        # Rebuild TF-IDF
        print("📊 Rebuilding TF-IDF index...")
        tfidf_matcher = waveseek_api.get_matcher('tfidf')
        tfidf_count = len(tfidf_matcher.songs_df)
        
        # Rebuild neural embeddings
        print("🧠 Rebuilding neural embeddings...")
        neural_matcher = waveseek_api.get_matcher('neural')
        neural_matcher.rebuild_embeddings()
        neural_count = len(neural_matcher.songs_df)
        
        print(f"\n✅ All indexes rebuilt successfully!")
        print(f"   TF-IDF: {tfidf_count} songs")
        print(f"   Neural: {neural_count} songs")
        
        return jsonify({
            'success': True,
            'message': 'All indexes rebuilt',
            'tfidf_songs': tfidf_count,
            'neural_songs': neural_count
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error: {error_details}")
        
        return jsonify({
            'error': str(e),
            'details': error_details
        }), 500
    

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
    print("🚀 WaveSeek API with GPU Acceleration")
    print("="*60)
    
    if GPU_AVAILABLE:
        GPUConfig.print_gpu_status()
        print("\n✅ GPU acceleration available for Premium tier")
    else:
        print("\n⚠️  GPU not available - CPU mode only")
    
    print(f"\n🌐 Running on: http://localhost:5000")
    print(f"🔗 GPU Status: http://localhost:5000/api/gpu/status")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)