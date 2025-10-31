"""
Hybrid Matcher combining Acoustic Fingerprinting + Neural Embeddings + TF-IDF
Location: src/hybrid_matcher.py
"""
import numpy as np
from collections import defaultdict

from config import Config
from src.fingerprinter import AcousticFingerprinter
from src.neural_matcher import NeuralLyricsMatcher
from src.matcher import LyricsMatcher
from src.database import LyricsDatabase


class HybridMatcher:
    """
    Combine multiple matching methods:
    1. Acoustic Fingerprinting (audio-based)
    2. Neural Embeddings (lyrics-based, semantic)
    3. TF-IDF (lyrics-based, keyword)
    """
    
    def __init__(self, use_fingerprint=True, use_neural=True, use_tfidf=True):
        """
        Initialize hybrid matcher
        
        Args:
            use_fingerprint: Enable acoustic fingerprinting
            use_neural: Enable neural embeddings
            use_tfidf: Enable TF-IDF matching
        """
        print("🔄 Initializing Hybrid Matcher...")
        
        self.use_fingerprint = use_fingerprint
        self.use_neural = use_neural
        self.use_tfidf = use_tfidf
        
        self.db = LyricsDatabase()
        self.songs_df = self.db.get_all_songs()
        
        # Initialize matchers
        self.fingerprinter = None
        self.neural_matcher = None
        self.tfidf_matcher = None
        
        if use_fingerprint:
            print("🔊 Loading Acoustic Fingerprinter...")
            self.fingerprinter = AcousticFingerprinter()
            # Note: Fingerprint database must be built separately
        
        if use_neural:
            print("🧠 Loading Neural Matcher...")
            self.neural_matcher = NeuralLyricsMatcher()
        
        if use_tfidf:
            print("📊 Loading TF-IDF Matcher...")
            self.tfidf_matcher = LyricsMatcher()
        
        print("✅ Hybrid Matcher ready")
    
    def match_with_audio(self, audio_path, transcribed_text=None, top_k=5,
                        fingerprint_weight=0.5, neural_weight=0.3, tfidf_weight=0.2):
        """
        Match using all available methods
        
        Args:
            audio_path: Path to audio file
            transcribed_text: Pre-transcribed lyrics (optional)
            top_k: Number of results to return
            fingerprint_weight: Weight for acoustic fingerprinting
            neural_weight: Weight for neural embeddings
            tfidf_weight: Weight for TF-IDF matching
        
        Returns:
            Combined results
        """
        # Normalize weights
        total_weight = fingerprint_weight + neural_weight + tfidf_weight
        fingerprint_weight /= total_weight
        neural_weight /= total_weight
        tfidf_weight /= total_weight
        
        print(f"\n🔍 Hybrid Matching with:")
        print(f"   🔊 Fingerprint: {fingerprint_weight:.1%}")
        print(f"   🧠 Neural: {neural_weight:.1%}")
        print(f"   📊 TF-IDF: {tfidf_weight:.1%}")
        
        all_scores = defaultdict(lambda: {
            'fingerprint': 0.0,
            'neural': 0.0,
            'tfidf': 0.0,
            'metadata': None
        })
        
        # 1. Acoustic Fingerprinting (if enabled and database exists)
        if self.use_fingerprint and self.fingerprinter:
            try:
                print("\n🔊 Step 1: Acoustic Fingerprinting...")
                fp_results = self.fingerprinter.match_audio(audio_path, top_k=top_k*2)
                
                if fp_results:
                    print(f"   ✅ Found {len(fp_results)} fingerprint matches")
                    for result in fp_results:
                        # Try to map filename to database song
                        song = self._find_song_by_filename(result['filename'])
                        if song:
                            song_key = f"{song['artist']}|{song['title']}"
                            all_scores[song_key]['fingerprint'] = result['fingerprint_score']
                            all_scores[song_key]['metadata'] = song
                else:
                    print("   ℹ️  No fingerprint matches")
            except Exception as e:
                print(f"   ⚠️  Fingerprinting error: {e}")
        
        # 2. Neural Embeddings (if transcription available)
        if self.use_neural and transcribed_text and self.neural_matcher:
            try:
                print("\n🧠 Step 2: Neural Semantic Matching...")
                neural_results = self.neural_matcher.match(transcribed_text, top_k=top_k*2)
                
                if neural_results:
                    print(f"   ✅ Found {len(neural_results)} neural matches")
                    for result in neural_results:
                        song_key = f"{result['artist']}|{result['title']}"
                        all_scores[song_key]['neural'] = result['final_score']
                        if all_scores[song_key]['metadata'] is None:
                            all_scores[song_key]['metadata'] = result
                else:
                    print("   ℹ️  No neural matches")
            except Exception as e:
                print(f"   ⚠️  Neural matching error: {e}")
        
        # 3. TF-IDF (if transcription available)
        if self.use_tfidf and transcribed_text and self.tfidf_matcher:
            try:
                print("\n📊 Step 3: TF-IDF Keyword Matching...")
                tfidf_results = self.tfidf_matcher.match(transcribed_text, top_k=top_k*2)
                
                if tfidf_results:
                    print(f"   ✅ Found {len(tfidf_results)} TF-IDF matches")
                    for result in tfidf_results:
                        song_key = f"{result['artist']}|{result['title']}"
                        all_scores[song_key]['tfidf'] = result['final_score']
                        if all_scores[song_key]['metadata'] is None:
                            all_scores[song_key]['metadata'] = result
                else:
                    print("   ℹ️  No TF-IDF matches")
            except Exception as e:
                print(f"   ⚠️  TF-IDF matching error: {e}")
        
        # Combine scores
        print(f"\n🔄 Combining results...")
        combined_results = []
        
        for song_key, scores in all_scores.items():
            # Calculate weighted final score
            final_score = (
                scores['fingerprint'] * fingerprint_weight +
                scores['neural'] * neural_weight +
                scores['tfidf'] * tfidf_weight
            )
            
            if scores['metadata']:
                result = scores['metadata'].copy()
                result['final_score'] = final_score
                result['fingerprint_score'] = scores['fingerprint']
                result['neural_score'] = scores['neural']
                result['tfidf_score'] = scores['tfidf']
                result['match_type'] = 'hybrid_multi_method'
                result['methods_used'] = []
                
                if scores['fingerprint'] > 0:
                    result['methods_used'].append('fingerprint')
                if scores['neural'] > 0:
                    result['methods_used'].append('neural')
                if scores['tfidf'] > 0:
                    result['methods_used'].append('tfidf')
                
                combined_results.append(result)
        
        # Sort by final score
        combined_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        print(f"✅ Combined {len(combined_results)} unique matches")
        
        return combined_results[:top_k]
    
    def match_lyrics_only(self, transcribed_text, top_k=5, 
                         neural_weight=0.6, tfidf_weight=0.4):
        """
        Match using only lyrics-based methods (no audio fingerprinting)
        
        Args:
            transcribed_text: Transcribed lyrics
            top_k: Number of results
            neural_weight: Weight for neural embeddings
            tfidf_weight: Weight for TF-IDF
        
        Returns:
            Combined results
        """
        # Normalize weights
        total = neural_weight + tfidf_weight
        neural_weight /= total
        tfidf_weight /= total
        
        print(f"\n🔍 Lyrics-Only Matching:")
        print(f"   🧠 Neural: {neural_weight:.1%}")
        print(f"   📊 TF-IDF: {tfidf_weight:.1%}")
        
        all_scores = defaultdict(lambda: {'neural': 0.0, 'tfidf': 0.0, 'metadata': None})
        
        # Neural matching
        if self.use_neural and self.neural_matcher:
            neural_results = self.neural_matcher.match(transcribed_text, top_k=top_k*2)
            for result in neural_results:
                song_key = f"{result['artist']}|{result['title']}"
                all_scores[song_key]['neural'] = result['final_score']
                all_scores[song_key]['metadata'] = result
        
        # TF-IDF matching
        if self.use_tfidf and self.tfidf_matcher:
            tfidf_results = self.tfidf_matcher.match(transcribed_text, top_k=top_k*2)
            for result in tfidf_results:
                song_key = f"{result['artist']}|{result['title']}"
                all_scores[song_key]['tfidf'] = result['final_score']
                if all_scores[song_key]['metadata'] is None:
                    all_scores[song_key]['metadata'] = result
        
        # Combine
        combined_results = []
        for song_key, scores in all_scores.items():
            final_score = (
                scores['neural'] * neural_weight +
                scores['tfidf'] * tfidf_weight
            )
            
            if scores['metadata']:
                result = scores['metadata'].copy()
                result['final_score'] = final_score
                result['neural_score'] = scores['neural']
                result['tfidf_score'] = scores['tfidf']
                result['match_type'] = 'hybrid_lyrics_only'
                combined_results.append(result)
        
        combined_results.sort(key=lambda x: x['final_score'], reverse=True)
        return combined_results[:top_k]
    
    def _find_song_by_filename(self, filename):
        """
        Try to match fingerprint filename to database song
        (This is a fallback - ideally fingerprints would be stored with song IDs)
        """
        # Remove extension
        from pathlib import Path
        name = Path(filename).stem.lower()
        
        # Search database for similar titles/artists
        for _, song in self.songs_df.iterrows():
            song_name = f"{song['artist']} {song['title']}".lower()
            if name in song_name or song_name in name:
                return {
                    'id': song['id'],
                    'artist': song['artist'],
                    'title': song['title'],
                    'album': song['album'],
                    'year': song['year']
                }
        
        return None
    
    def get_match_summary(self, results):
        """Generate formatted summary of hybrid matches"""
        if not results:
            return "❌ No matches found"
        
        summary = f"\n{'='*60}\n"
        summary += f"🎯 Hybrid Multi-Method Matches\n"
        summary += f"{'='*60}\n\n"
        
        for i, result in enumerate(results, 1):
            confidence = self._get_confidence_level(result['final_score'])
            
            summary += f"{i}. 🎤 {result['artist']} - {result['title']}\n"
            if result.get('album'):
                summary += f"   💿 Album: {result['album']}\n"
            if result.get('year'):
                summary += f"   📅 Year: {result['year']}\n"
            
            summary += f"   📊 Final Score: {result['final_score']:.2%} ({confidence})\n"
            summary += f"   🔬 Method: {result['match_type']}\n"
            
            # Show individual method scores
            if 'fingerprint_score' in result and result['fingerprint_score'] > 0:
                summary += f"   🔊 Fingerprint: {result['fingerprint_score']:.2%}\n"
            if 'neural_score' in result and result['neural_score'] > 0:
                summary += f"   🧠 Neural: {result['neural_score']:.2%}\n"
            if 'tfidf_score' in result and result['tfidf_score'] > 0:
                summary += f"   📊 TF-IDF: {result['tfidf_score']:.2%}\n"
            
            if 'methods_used' in result:
                summary += f"   ✅ Methods: {', '.join(result['methods_used'])}\n"
            
            summary += "\n"
        
        return summary
    
    def _get_confidence_level(self, score):
        """Get confidence description"""
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
        """Close all connections"""
        if self.fingerprinter:
            self.fingerprinter.close()
        if self.neural_matcher:
            self.neural_matcher.close()
        if self.tfidf_matcher:
            self.tfidf_matcher.close()
        self.db.close()


def test_hybrid_matcher():
    """Test hybrid matching"""
    print("\n" + "="*60)
    print("Testing Hybrid Multi-Method Matcher")
    print("="*60 + "\n")
    
    matcher = HybridMatcher(
        use_fingerprint=True,
        use_neural=True,
        use_tfidf=True
    )
    
    # Test with lyrics only
    test_query = "feeling good today sunshine bright sky"
    print(f"Test Query: \"{test_query}\"")
    
    results = matcher.match_lyrics_only(test_query, top_k=3)
    print(matcher.get_match_summary(results))
    
    matcher.close()


if __name__ == "__main__":
    test_hybrid_matcher()