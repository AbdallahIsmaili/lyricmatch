"""
Enhanced lyrics matching engine using Sentence-BERT embeddings
Provides better semantic understanding than TF-IDF alone
"""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from tqdm import tqdm
import pickle
from pathlib import Path

from config import Config
from src.database import LyricsDatabase
from src.text_processor import TextProcessor


class NeuralLyricsMatcher:
    """Match transcribed lyrics using neural embeddings (SBERT)"""
    
    def __init__(self, db_path=None, model_name='all-MiniLM-L6-v2', use_cache=True):
        """
        Initialize neural matcher with SBERT
        
        Args:
            db_path: Path to lyrics database
            model_name: Sentence-BERT model to use
                Options:
                - 'all-MiniLM-L6-v2' (default): Fast, 384 dims, good quality
                - 'all-mpnet-base-v2': Best quality, 768 dims, slower
                - 'paraphrase-MiniLM-L6-v2': Good for paraphrases
            use_cache: Cache embeddings to disk for faster loading
        """
        print("🔄 Initializing NeuralLyricsMatcher with Sentence-BERT...")
        
        self.db = LyricsDatabase(db_path)
        self.text_processor = TextProcessor(remove_stopwords=False, lowercase=True)
        self.use_cache = use_cache
        self.model_name = model_name
        
        # Load all songs from database
        self.songs_df = self._load_songs()
        
        if self.songs_df.empty:
            raise ValueError("No songs found in database. Run setup_database.py first.")
        
        print(f"✅ Loaded {len(self.songs_df)} songs from database")
        
        # Initialize Sentence-BERT model
        print(f"📥 Loading Sentence-BERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded successfully")
        
        # Build or load embeddings
        self.embeddings = None
        self._build_embeddings()
    
    def _load_songs(self):
        """Load songs from database into DataFrame"""
        songs = self.db.get_all_songs()
        df = pd.DataFrame(songs)
        
        # Ensure lyrics_cleaned exists
        if 'lyrics_cleaned' not in df.columns or df['lyrics_cleaned'].isna().all():
            df['lyrics_cleaned'] = df['lyrics'].apply(self.text_processor.clean_text)
        
        return df
    
    def _get_cache_path(self):
        """Get path for cached embeddings"""
        cache_dir = Config.MODELS_DIR / "embeddings_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create cache filename based on model and data
        cache_name = f"{self.model_name.replace('/', '_')}_{len(self.songs_df)}_songs.pkl"
        return cache_dir / cache_name
    
    def _build_embeddings(self):
        """Build or load neural embeddings for all songs"""
        cache_path = self._get_cache_path()
        
        # Try to load from cache
        if self.use_cache and cache_path.exists():
            try:
                print(f"📦 Loading cached embeddings from: {cache_path.name}")
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                    
                # Verify cache is valid
                if len(cache_data['embeddings']) == len(self.songs_df):
                    self.embeddings = cache_data['embeddings']
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from cache")
                    return
                else:
                    print("⚠️  Cache size mismatch, rebuilding embeddings...")
            except Exception as e:
                print(f"⚠️  Error loading cache: {e}")
                print("   Rebuilding embeddings...")
        
        # Build embeddings from scratch
        print("🔨 Building neural embeddings (this may take a few minutes)...")
        
        lyrics_list = self.songs_df['lyrics_cleaned'].tolist()
        
        # Encode in batches with progress bar
        batch_size = 32
        embeddings_list = []
        
        for i in tqdm(range(0, len(lyrics_list), batch_size), desc="Encoding lyrics"):
            batch = lyrics_list[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings_list.append(batch_embeddings)
        
        self.embeddings = np.vstack(embeddings_list)
        
        print(f"✅ Built embeddings: shape {self.embeddings.shape}")
        
        # Save to cache
        if self.use_cache:
            try:
                print(f"💾 Saving embeddings to cache...")
                cache_data = {
                    'embeddings': self.embeddings,
                    'model_name': self.model_name,
                    'num_songs': len(self.songs_df)
                }
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                print(f"✅ Cache saved: {cache_path}")
            except Exception as e:
                print(f"⚠️  Error saving cache: {e}")
    
    def match(self, query_text, top_k=None, use_fuzzy=None, hybrid_weight=0.7):
        """
        Match query text against song database using neural embeddings
        
        Args:
            query_text: Transcribed lyrics to match
            top_k: Number of top results to return
            use_fuzzy: Use fuzzy matching for refinement
            hybrid_weight: Weight for neural embeddings (0-1)
                          1.0 = pure neural, 0.0 = pure fuzzy
        
        Returns:
            List of matching songs with scores
        """
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        if use_fuzzy is None:
            use_fuzzy = Config.USE_FUZZY_MATCHING
        
        # Clean query text
        query_cleaned = self.text_processor.clean_text(query_text)
        
        if not query_cleaned:
            return []
        
        print(f"\n🔍 Searching with neural embeddings: \"{query_cleaned[:100]}...\"")
        
        # Neural embedding matching
        results = self._neural_match(query_cleaned, top_k * 2)
        
        # Apply fuzzy matching if enabled for hybrid approach
        if use_fuzzy and results:
            results = self._hybrid_refinement(
                query_cleaned, 
                results, 
                top_k,
                neural_weight=hybrid_weight
            )
        else:
            results = results[:top_k]
        
        return results
    
    def _neural_match(self, query_text, top_k):
        """
        Match using neural embeddings and cosine similarity
        
        Args:
            query_text: Cleaned query text
            top_k: Number of results
        
        Returns:
            List of matches with neural scores
        """
        # Encode query
        query_embedding = self.model.encode(
            [query_text],
            convert_to_numpy=True
        )
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Filter by threshold
        results = []
        for idx in top_indices:
            score = similarities[idx]
            
            # Use lower threshold for neural embeddings (they're more nuanced)
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
                    'match_type': 'neural_embedding'
                })
        
        return results
    
    def _hybrid_refinement(self, query_text, candidates, top_k, neural_weight=0.7):
        """
        Refine results using hybrid neural + fuzzy matching
        
        Args:
            query_text: Query text
            candidates: Initial candidate matches
            top_k: Number of final results
            neural_weight: Weight for neural score (vs fuzzy)
        
        Returns:
            Refined list of matches
        """
        fuzzy_weight = 1.0 - neural_weight
        
        for candidate in candidates:
            song_id = candidate['id']
            song_lyrics = self.songs_df[self.songs_df['id'] == song_id]['lyrics_cleaned'].iloc[0]
            
            # Calculate fuzzy scores
            partial_score = fuzz.partial_ratio(query_text, song_lyrics) / 100
            token_sort_score = fuzz.token_sort_ratio(query_text, song_lyrics) / 100
            token_set_score = fuzz.token_set_ratio(query_text, song_lyrics) / 100
            
            # Weighted combination of fuzzy scores
            fuzzy_score = (partial_score * 0.4 + 
                          token_sort_score * 0.3 + 
                          token_set_score * 0.3)
            
            # Hybrid combination: neural + fuzzy
            candidate['fuzzy_score'] = fuzzy_score
            candidate['final_score'] = (
                candidate['neural_score'] * neural_weight + 
                fuzzy_score * fuzzy_weight
            )
            candidate['match_type'] = 'hybrid_neural+fuzzy'
        
        # Sort by final score
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        return candidates[:top_k]
    
    def match_with_details(self, query_text, top_k=None):
        """
        Match with detailed information about the match
        
        Args:
            query_text: Query text
            top_k: Number of results
        
        Returns:
            List of detailed matches
        """
        results = self.match(query_text, top_k)
        
        # Add additional details
        for result in results:
            song_id = result['id']
            song = self.songs_df[self.songs_df['id'] == song_id].iloc[0]
            
            # Add word counts
            result['query_word_count'] = len(query_text.split())
            result['song_word_count'] = song['word_count']
            
            # Calculate match percentage
            query_words = set(query_text.split())
            song_words = set(song['lyrics_cleaned'].split())
            common_words = query_words.intersection(song_words)
            
            result['common_word_count'] = len(common_words)
            result['match_percentage'] = (len(common_words) / len(query_words) * 100 
                                         if query_words else 0)
        
        return results
    
    def get_match_summary(self, results):
        """
        Generate summary of match results
        
        Args:
            results: List of match results
        
        Returns:
            Formatted summary string
        """
        if not results:
            return "❌ No matches found"
        
        summary = f"\n{'='*60}\n"
        summary += f"🎵 Found {len(results)} match(es) using Neural Embeddings\n"
        summary += f"{'='*60}\n\n"
        
        for i, result in enumerate(results, 1):
            confidence = self._get_confidence_level(result['final_score'])
            
            summary += f"{i}. 🎤 {result['artist']} - {result['title']}\n"
            if result.get('album'):
                summary += f"   💿 Album: {result['album']}\n"
            if result.get('year'):
                summary += f"   📅 Year: {result['year']}\n"
            summary += f"   📊 Score: {result['final_score']:.2%} ({confidence})\n"
            summary += f"   🔬 Match Type: {result['match_type']}\n"
            
            if result.get('neural_score'):
                summary += f"   🧠 Neural Score: {result['neural_score']:.2%}\n"
            if result.get('fuzzy_score'):
                summary += f"   🔤 Fuzzy Score: {result['fuzzy_score']:.2%}\n"
            
            if 'match_percentage' in result:
                summary += f"   ✨ Word Match: {result['match_percentage']:.1f}%\n"
            
            summary += "\n"
        
        return summary
    
    def _get_confidence_level(self, score):
        """Get confidence level description"""
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
    
    def compare_with_tfidf(self, query_text, top_k=5):
        """
        Compare neural embeddings with TF-IDF approach
        Useful for evaluation and debugging
        
        Returns:
            Dictionary with both results
        """
        from src.matcher import LyricsMatcher
        
        print("\n" + "="*60)
        print("🔬 Comparing Neural vs TF-IDF Matching")
        print("="*60)
        
        # Neural results
        print("\n🧠 Neural Embeddings Results:")
        neural_results = self.match_with_details(query_text, top_k)
        print(self.get_match_summary(neural_results))
        
        # TF-IDF results
        print("\n📊 TF-IDF Results:")
        tfidf_matcher = LyricsMatcher()
        tfidf_results = tfidf_matcher.match_with_details(query_text, top_k)
        print(tfidf_matcher.get_match_summary(tfidf_results))
        tfidf_matcher.close()
        
        return {
            'neural': neural_results,
            'tfidf': tfidf_results
        }
    
    def rebuild_embeddings(self):
        """Force rebuild of embeddings (e.g., after database update)"""
        print("🔄 Rebuilding embeddings...")
        cache_path = self._get_cache_path()
        if cache_path.exists():
            cache_path.unlink()
        self._build_embeddings()
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_neural_matcher():
    """Test the neural matcher with sample queries"""
    print("\n" + "="*60)
    print("Testing Neural Lyrics Matcher (SBERT)")
    print("="*60 + "\n")
    
    try:
        # Initialize with default model (fast, good quality)
        matcher = NeuralLyricsMatcher(model_name='all-MiniLM-L6-v2')
        
        # Test queries
        test_queries = [
            "feeling good today sun shining bright",
            "love me tender love me sweet",
            "we will rock you stomp stomp clap"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Test Query {i}: \"{query}\"")
            print(f"{'='*60}")
            
            results = matcher.match_with_details(query, top_k=3)
            print(matcher.get_match_summary(results))
        
        # Optional: Compare with TF-IDF
        print("\n" + "="*60)
        print("🔬 Comparison Test (Neural vs TF-IDF)")
        print("="*60)
        
        comparison = matcher.compare_with_tfidf(test_queries[0], top_k=3)
        
        matcher.close()
        
        print("\n✅ Neural matcher test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_neural_matcher()