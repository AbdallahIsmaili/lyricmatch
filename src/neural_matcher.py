"""
Enhanced lyrics matching with GPU-accelerated Sentence-BERT
Optimized for NVIDIA RTX 3060 6GB
Location: src/neural_matcher.py (UPDATED)
"""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from tqdm import tqdm
import pickle
from pathlib import Path
import time
import torch

from config import Config
from src.database import LyricsDatabase
from src.text_processor import TextProcessor

# Import GPU config
try:
    from gpu_config import GPUConfig
    GPU_AVAILABLE = True
except ImportError:
    print("⚠️  GPU config not found - using CPU mode")
    GPU_AVAILABLE = False
    class GPUConfig:
        DEVICE = "cpu"
        SBERT_BATCH_SIZE_GPU = 16
        SBERT_BATCH_SIZE_CPU = 16


class NeuralLyricsMatcher:
    """GPU-accelerated neural lyrics matcher with SBERT"""
    
    def __init__(self, db_path=None, model_name='all-MiniLM-L6-v2', 
                 use_cache=True, use_gpu=True, force_cpu=False):
        """
        Initialize neural matcher with GPU support
        
        Args:
            db_path: Path to lyrics database
            model_name: SBERT model name
            use_cache: Cache embeddings
            use_gpu: Use GPU if available
            force_cpu: Force CPU mode
        """
        print("📄 Initializing GPU-Accelerated Neural Matcher...")
        
        self.db = LyricsDatabase(db_path)
        self.text_processor = TextProcessor(remove_stopwords=False, lowercase=True)
        self.use_cache = use_cache
        self.model_name = model_name
        self.use_gpu = use_gpu and GPU_AVAILABLE and not force_cpu
        
        # Load songs
        self.songs_df = self._load_songs()
        
        if self.songs_df.empty:
            raise ValueError("No songs in database")
        
        print(f"✅ Loaded {len(self.songs_df)} songs")
        
        # Determine device and batch size
        if force_cpu:
            self.device = "cpu"
            self.batch_size = GPUConfig.SBERT_BATCH_SIZE_CPU
            self.use_fp16 = False
            print("🖥️  Forced CPU mode")
        elif self.use_gpu:
            safety = GPUConfig.check_model_safety('sbert', model_name)
            
            if safety.get('safe', False):
                self.device = GPUConfig.DEVICE
                self.batch_size = GPUConfig.SBERT_BATCH_SIZE_GPU
                self.use_fp16 = GPUConfig.SBERT_FP16 and self.device == "cuda"
                print(f"🎮 GPU mode enabled for SBERT")
                print(f"   Device: {self.device}")
                print(f"   Batch size: {self.batch_size}")
                print(f"   FP16: {self.use_fp16}")
            else:
                self.device = "cpu"
                self.batch_size = GPUConfig.SBERT_BATCH_SIZE_CPU
                self.use_fp16 = False
                print(f"⚠️  GPU unsafe: {safety.get('reason', 'Unknown')}")
                print(f"   Using CPU mode")
        else:
            self.device = "cpu"
            self.batch_size = GPUConfig.SBERT_BATCH_SIZE_CPU
            self.use_fp16 = False
        
        # Load SBERT model
        print(f"📥 Loading SBERT: {model_name}")
        start_time = time.time()
        
        self.model = SentenceTransformer(model_name, device=self.device)
        
        # Enable FP16 if using GPU
        if self.use_fp16 and self.device == "cuda":
            self.model = self.model.half()
            print("   ✅ FP16 mode enabled")
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")
        
        # Show GPU status
        if self.device == "cuda" and GPU_AVAILABLE:
            gpu_info = GPUConfig.get_gpu_info()
            print(f"   VRAM allocated: {gpu_info['memory_allocated_gb']:.2f}GB")
            temp = gpu_info.get('temperature_c')
            if temp is not None:
                print(f"   GPU temp: {temp}°C")
        
        # Build embeddings
        self.embeddings = None
        self._build_embeddings()
    
    def _load_songs(self):
        """Load songs from database"""
        songs = self.db.get_all_songs()
        df = pd.DataFrame(songs)
        
        if 'lyrics_cleaned' not in df.columns or df['lyrics_cleaned'].isna().all():
            df['lyrics_cleaned'] = df['lyrics'].apply(self.text_processor.clean_text)
        
        return df
    
    def _get_cache_path(self):
        """Get embeddings cache path"""
        cache_dir = Config.MODELS_DIR / "embeddings_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Include device and precision in cache name
        device_suffix = f"_{self.device}"
        if self.use_fp16:
            device_suffix += "_fp16"
        
        cache_name = f"{self.model_name.replace('/', '_')}_{len(self.songs_df)}_songs{device_suffix}.pkl"
        return cache_dir / cache_name
    
    def _build_embeddings(self):
        """Build or load embeddings with GPU acceleration"""
        cache_path = self._get_cache_path()
        
        # Try cache
        if self.use_cache and cache_path.exists():
            try:
                print(f"📦 Loading cached embeddings: {cache_path.name}")
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if len(cache_data['embeddings']) == len(self.songs_df):
                    self.embeddings = cache_data['embeddings']
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from cache")
                    return
                else:
                    print("⚠️  Cache size mismatch, rebuilding...")
            except Exception as e:
                print(f"⚠️  Cache load failed: {e}")
        
        # Build embeddings from scratch
        print(f"🔨 Building embeddings with GPU acceleration...")
        print(f"   Device: {self.device} | Batch: {self.batch_size} | FP16: {self.use_fp16}")
        
        lyrics_list = self.songs_df['lyrics_cleaned'].tolist()
        
        start_time = time.time()
        embeddings_list = []
        
        # Encode with progress bar
        for i in tqdm(range(0, len(lyrics_list), self.batch_size), desc="Encoding"):
            batch = lyrics_list[i:i + self.batch_size]
            
            # Monitor GPU temperature
            if self.device == "cuda" and GPU_AVAILABLE and i % 500 == 0:
                gpu_info = GPUConfig.get_gpu_info()
                temp = gpu_info.get('temperature_c')
                if temp is not None and temp > GPUConfig.THROTTLE_TEMP:
                    print(f"\n⚠️  GPU hot ({gpu_info['temperature_c']}°C), cooling...")
                    time.sleep(2)
                    GPUConfig.clear_gpu_cache()
            
            batch_embeddings = self.model.encode(
                batch,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # Faster cosine similarity
            )
            
            embeddings_list.append(batch_embeddings)
        
        self.embeddings = np.vstack(embeddings_list)
        
        build_time = time.time() - start_time
        print(f"✅ Built {self.embeddings.shape[0]} embeddings in {build_time:.2f}s")
        print(f"   Shape: {self.embeddings.shape}")
        print(f"   Speed: {len(lyrics_list) / build_time:.1f} songs/sec")
        
        # GPU stats
        if self.device == "cuda" and GPU_AVAILABLE:
            gpu_info = GPUConfig.get_gpu_info()
            print(f"   VRAM used: {gpu_info['memory_allocated_gb']:.2f}GB")
            if gpu_info.get('temperature_c'):
                print(f"   GPU temp: {gpu_info['temperature_c']}°C")
        
        # Save cache
        if self.use_cache:
            try:
                print(f"💾 Saving to cache...")
                cache_data = {
                    'embeddings': self.embeddings,
                    'model_name': self.model_name,
                    'num_songs': len(self.songs_df),
                    'device': self.device,
                    'fp16': self.use_fp16
                }
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                print(f"✅ Cache saved: {cache_path}")
            except Exception as e:
                print(f"⚠️  Cache save failed: {e}")
    
    def match(self, query_text, top_k=None, use_fuzzy=None, hybrid_weight=0.7):
        """
        Match query with GPU acceleration
        
        Args:
            query_text: Query lyrics
            top_k: Number of results
            use_fuzzy: Use fuzzy refinement
            hybrid_weight: Neural vs fuzzy weight
        
        Returns:
            List of matches
        """
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        if use_fuzzy is None:
            use_fuzzy = Config.USE_FUZZY_MATCHING
        
        query_cleaned = self.text_processor.clean_text(query_text)
        
        if not query_cleaned:
            return []
        
        print(f"\n🔍 Searching with GPU neural embeddings...")
        
        # Neural matching
        results = self._neural_match(query_cleaned, top_k * 2)
        
        # Fuzzy refinement
        if use_fuzzy and results:
            results = self._hybrid_refinement(
                query_cleaned, results, top_k, neural_weight=hybrid_weight
            )
        else:
            results = results[:top_k]
        
        return results
    
    def _neural_match(self, query_text, top_k):
        """GPU-accelerated neural matching"""
        start_time = time.time()
        
        # Encode query
        query_embedding = self.model.encode(
            [query_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Cosine similarity (faster with normalized embeddings)
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        
        # Top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        match_time = time.time() - start_time
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            
            if score >= Config.SIMILARITY_THRESHOLD * 0.8:
                song = self.songs_df.iloc[idx]
                results.append({
                    'id': int(song['id']),
                    'artist': song['artist'],
                    'title': song['title'],
                    'album': song['album'],
                    'year': song['year'],
                    'neural_score': float(score),
                    'final_score': float(score),
                    'match_type': 'neural_embedding',
                    'device_used': self.device,
                    'match_time_ms': round(match_time * 1000, 2)
                })
        
        print(f"   Matching time: {match_time*1000:.1f}ms on {self.device}")
        
        return results
    
    def _hybrid_refinement(self, query_text, candidates, top_k, neural_weight=0.7):
        """Hybrid neural + fuzzy refinement"""
        fuzzy_weight = 1.0 - neural_weight
        
        for candidate in candidates:
            song_id = candidate['id']
            song_lyrics = self.songs_df[self.songs_df['id'] == song_id]['lyrics_cleaned'].iloc[0]
            
            # Fuzzy scores
            partial = fuzz.partial_ratio(query_text, song_lyrics) / 100
            token_sort = fuzz.token_sort_ratio(query_text, song_lyrics) / 100
            token_set = fuzz.token_set_ratio(query_text, song_lyrics) / 100
            
            fuzzy_score = partial * 0.4 + token_sort * 0.3 + token_set * 0.3
            
            # Combine
            candidate['fuzzy_score'] = fuzzy_score
            candidate['final_score'] = (
                candidate['neural_score'] * neural_weight + 
                fuzzy_score * fuzzy_weight
            )
            candidate['match_type'] = 'hybrid_neural+fuzzy'
        
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        return candidates[:top_k]
    
    def match_with_details(self, query_text, top_k=None):
        """Match with detailed info"""
        results = self.match(query_text, top_k)
        
        for result in results:
            song_id = result['id']
            song = self.songs_df[self.songs_df['id'] == song_id].iloc[0]
            
            result['query_word_count'] = len(query_text.split())
            result['song_word_count'] = song['word_count']
            
            query_words = set(query_text.split())
            song_words = set(song['lyrics_cleaned'].split())
            common_words = query_words.intersection(song_words)
            
            result['common_word_count'] = len(common_words)
            result['match_percentage'] = (
                len(common_words) / len(query_words) * 100 if query_words else 0
            )
        
        return results
    
    def get_match_summary(self, results):
        """Generate match summary"""
        if not results:
            return "❌ No matches found"
        
        summary = f"\n{'='*60}\n"
        summary += f"🎵 Found {len(results)} match(es) - GPU Neural Embeddings\n"
        summary += f"{'='*60}\n\n"
        
        for i, result in enumerate(results, 1):
            confidence = self._get_confidence_level(result['final_score'])
            
            summary += f"{i}. 🎤 {result['artist']} - {result['title']}\n"
            if result.get('album'):
                summary += f"   💿 Album: {result['album']}\n"
            if result.get('year'):
                summary += f"   📅 Year: {result['year']}\n"
            summary += f"   📊 Score: {result['final_score']:.2%} ({confidence})\n"
            summary += f"   🔬 Type: {result['match_type']}\n"
            summary += f"   ⚡ Device: {result.get('device_used', 'unknown')}\n"
            
            if result.get('match_time_ms'):
                summary += f"   ⏱️  Time: {result['match_time_ms']}ms\n"
            
            if result.get('neural_score'):
                summary += f"   🧠 Neural: {result['neural_score']:.2%}\n"
            if result.get('fuzzy_score'):
                summary += f"   🔤 Fuzzy: {result['fuzzy_score']:.2%}\n"
            
            if 'match_percentage' in result:
                summary += f"   ✨ Words: {result['match_percentage']:.1f}%\n"
            
            summary += "\n"
        
        return summary
    
    def _get_confidence_level(self, score):
        """Get confidence description"""
        if score >= 0.75:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.45:
            return "Medium"
        elif score >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def rebuild_embeddings(self):
        """Force rebuild embeddings"""
        print("🔄 Rebuilding embeddings...")
        cache_path = self._get_cache_path()
        if cache_path.exists():
            cache_path.unlink()
        self._build_embeddings()
    
    def get_performance_info(self):
        """Get performance configuration"""
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'batch_size': self.batch_size,
            'fp16_enabled': self.use_fp16,
            'num_embeddings': len(self.embeddings) if self.embeddings is not None else 0,
            'embedding_dim': self.embeddings.shape[1] if self.embeddings is not None else 0
        }
        
        if self.device == "cuda" and GPU_AVAILABLE:
            gpu_info = GPUConfig.get_gpu_info()
            info['gpu_name'] = gpu_info.get('name', 'Unknown')
            info['vram_allocated_gb'] = gpu_info.get('memory_allocated_gb', 0)
            info['vram_free_gb'] = gpu_info.get('memory_free_gb', 0)
            info['temperature_c'] = gpu_info.get('temperature_c')
        
        return info
    
    def cleanup(self):
        """Clean up GPU resources"""
        if self.device == "cuda" and GPU_AVAILABLE:
            del self.model
            if self.embeddings is not None:
                del self.embeddings
            GPUConfig.clear_gpu_cache()
            print("🧹 GPU cache cleared")
    
    def close(self):
        """Close database"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        self.close()


def test_neural_matcher():
    """Test GPU-accelerated neural matcher"""
    print("\n" + "="*60)
    print("Testing GPU-Accelerated Neural Matcher")
    print("="*60 + "\n")
    
    if GPU_AVAILABLE:
        GPUConfig.print_gpu_status()
    
    # Test with default model
    matcher = NeuralLyricsMatcher(model_name='all-MiniLM-L6-v2', use_gpu=True)
    
    # Show performance
    perf = matcher.get_performance_info()
    print(f"\n⚙️  Performance Config:")
    for key, value in perf.items():
        print(f"   {key}: {value}")
    
    # Test query
    test_query = "feeling good today sunshine bright"
    print(f"\n{'='*60}")
    print(f"Test Query: \"{test_query}\"")
    print(f"{'='*60}")
    
    results = matcher.match_with_details(test_query, top_k=3)
    print(matcher.get_match_summary(results))
    
    matcher.cleanup()


if __name__ == "__main__":
    test_neural_matcher()