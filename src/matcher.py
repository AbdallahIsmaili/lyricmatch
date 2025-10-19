"""
Lyrics matching engine using TF-IDF and similarity algorithms
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

from config import Config
from src.database import LyricsDatabase
from src.text_processor import TextProcessor


class LyricsMatcher:
    """Match transcribed lyrics to song database"""
    
    def __init__(self, db_path=None):
        """
        Initialize matcher with database
        
        Args:
            db_path: Path to lyrics database
        """
        print("🔄 Initializing LyricsMatcher...")
        
        self.db = LyricsDatabase(db_path)
        self.text_processor = TextProcessor(remove_stopwords=False, lowercase=True)
        
        # Load all songs from database
        self.songs_df = self._load_songs()
        
        if self.songs_df.empty:
            raise ValueError("No songs found in database. Run setup_database.py first.")
        
        print(f"✅ Loaded {len(self.songs_df)} songs from database")
        
        # Initialize vectorizer
        self.vectorizer = None
        self.tfidf_matrix = None
        
        # Build index
        self._build_index()
    
    def _load_songs(self):
        """Load songs from database into DataFrame"""
        songs = self.db.get_all_songs()
        df = pd.DataFrame(songs)
        
        # Ensure lyrics_cleaned exists
        if 'lyrics_cleaned' not in df.columns or df['lyrics_cleaned'].isna().all():
            df['lyrics_cleaned'] = df['lyrics'].apply(self.text_processor.clean_text)
        
        return df
    
    def _build_index(self):
        """Build TF-IDF index for fast searching"""
        print("🔄 Building TF-IDF index...")
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=Config.MAX_FEATURES,
            ngram_range=Config.NGRAM_RANGE,
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
        # Fit and transform lyrics
        lyrics_list = self.songs_df['lyrics_cleaned'].tolist()
        self.tfidf_matrix = self.vectorizer.fit_transform(lyrics_list)
        
        print(f"✅ Index built with {self.tfidf_matrix.shape[1]} features")
    
    def match(self, query_text, top_k=None, use_fuzzy=None):
        """
        Match query text against song database
        
        Args:
            query_text: Transcribed lyrics to match
            top_k: Number of top results to return
            use_fuzzy: Use fuzzy matching for refinement
        
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
        
        print(f"\n🔍 Searching for: \"{query_cleaned[:100]}...\"")
        
        # TF-IDF matching
        results = self._tfidf_match(query_cleaned, top_k * 2)  # Get more for fuzzy refinement
        
        # Apply fuzzy matching if enabled
        if use_fuzzy and results:
            results = self._fuzzy_refinement(query_cleaned, results, top_k)
        else:
            results = results[:top_k]
        
        return results
    
    def _tfidf_match(self, query_text, top_k):
        """
        Match using TF-IDF and cosine similarity
        
        Args:
            query_text: Cleaned query text
            top_k: Number of results
        
        Returns:
            List of matches
        """
        # Transform query
        query_vec = self.vectorizer.transform([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Filter by threshold
        results = []
        for idx in top_indices:
            score = similarities[idx]
            
            if score >= Config.SIMILARITY_THRESHOLD:
                song = self.songs_df.iloc[idx]
                results.append({
                    'id': int(song['id']),
                    'artist': song['artist'],
                    'title': song['title'],
                    'album': song['album'],
                    'year': song['year'],
                    'tfidf_score': float(score),
                    'final_score': float(score),
                    'match_type': 'tfidf'
                })
        
        return results
    
    def _fuzzy_refinement(self, query_text, candidates, top_k):
        """
        Refine results using fuzzy string matching
        
        Args:
            query_text: Query text
            candidates: Initial candidate matches
            top_k: Number of final results
        
        Returns:
            Refined list of matches
        """
        for candidate in candidates:
            song_id = candidate['id']
            song_lyrics = self.songs_df[self.songs_df['id'] == song_id]['lyrics_cleaned'].iloc[0]
            
            # Calculate fuzzy scores
            partial_score = fuzz.partial_ratio(query_text, song_lyrics) / 100
            token_sort_score = fuzz.token_sort_ratio(query_text, song_lyrics) / 100
            token_set_score = fuzz.token_set_ratio(query_text, song_lyrics) / 100
            
            # Weighted combination
            fuzzy_score = (partial_score * 0.4 + 
                          token_sort_score * 0.3 + 
                          token_set_score * 0.3)
            
            # Combine with TF-IDF score
            candidate['fuzzy_score'] = fuzzy_score
            candidate['final_score'] = (candidate['tfidf_score'] * 0.6 + fuzzy_score * 0.4)
            candidate['match_type'] = 'tfidf+fuzzy'
        
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
    
    def search_by_phrase(self, phrase):
        """
        Search for exact phrase in lyrics
        
        Args:
            phrase: Phrase to search
        
        Returns:
            List of songs containing the phrase
        """
        phrase_clean = self.text_processor.clean_text(phrase)
        
        matches = []
        for _, song in self.songs_df.iterrows():
            if phrase_clean in song['lyrics_cleaned']:
                matches.append({
                    'id': int(song['id']),
                    'artist': song['artist'],
                    'title': song['title'],
                    'album': song['album'],
                    'year': song['year'],
                    'match_type': 'exact_phrase'
                })
        
        return matches
    
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
        summary += f"🎵 Found {len(results)} match(es)\n"
        summary += f"{'='*60}\n\n"
        
        for i, result in enumerate(results, 1):
            confidence = self._get_confidence_level(result['final_score'])
            
            summary += f"{i}. 🎤 {result['artist']} - {result['title']}\n"
            if result.get('album'):
                summary += f"   💿 Album: {result['album']}\n"
            if result.get('year'):
                summary += f"   📅 Year: {result['year']}\n"
            summary += f"   📊 Score: {result['final_score']:.2%} ({confidence})\n"
            summary += f"   🔍 Match Type: {result['match_type']}\n"
            
            if 'match_percentage' in result:
                summary += f"   ✨ Word Match: {result['match_percentage']:.1f}%\n"
            
            summary += "\n"
        
        return summary
    
    def _get_confidence_level(self, score):
        """Get confidence level description"""
        if score >= 0.7:
            return "Very High"
        elif score >= 0.5:
            return "High"
        elif score >= 0.3:
            return "Medium"
        elif score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_matcher():
    """Test the matcher with sample queries"""
    print("\n" + "="*60)
    print("Testing Lyrics Matcher")
    print("="*60 + "\n")
    
    try:
        matcher = LyricsMatcher()
        
        # Test query (generic example, not actual lyrics)
        test_query = "feeling good today sun is shining bright"
        
        print(f"Test query: \"{test_query}\"")
        
        results = matcher.match_with_details(test_query, top_k=3)
        
        print(matcher.get_match_summary(results))
        
        matcher.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to run: python setup_database.py first")


if __name__ == "__main__":
    test_matcher()