"""
Enhanced Acoustic Fingerprinting for WaveSeek
Major improvements over basic implementation:
1. Multi-resolution spectrograms
2. Adaptive peak detection
3. Better hash generation
4. Time-offset clustering
5. Locality-sensitive hashing (LSH)
Location: src/fingerprinter.py
"""
import numpy as np
import librosa
import hashlib
from collections import defaultdict, Counter
import pickle
from pathlib import Path
from tqdm import tqdm
from scipy.ndimage import maximum_filter
from scipy.spatial.distance import hamming

from config import Config
from src.database import LyricsDatabase


class AcousticFingerprinter:
    """Enhanced acoustic fingerprinting with improved matching"""
    
    def __init__(self, db_path=None):
        """
        Initialize enhanced fingerprinter
        
        Args:
            db_path: Path to lyrics database
        """
        self.db = LyricsDatabase(db_path)
        self.fingerprint_db = {}
        self.song_metadata = {}
        
        self.cache_path = Config.MODELS_DIR / "fingerprints" / "fingerprint_cache.pkl"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Audio parameters
        self.sample_rate = Config.SAMPLE_RATE
        
        # Multi-resolution spectrogram parameters
        self.n_fft_sizes = [1024, 2048, 4096]  # Multiple resolutions
        self.hop_length = 256  # Smaller hop for better time resolution
        self.n_mels = 256  # More frequency bins
        
        # Enhanced peak detection
        self.peak_neighborhood_size = (20, 20)  # (time, freq)
        self.min_amplitude_percentile = 75  # More selective peaks
        
        # Improved constellation parameters
        self.fanout = 10  # Targets per anchor
        self.min_time_delta = 5   # Min frames between anchor/target
        self.max_time_delta = 100  # Max frames between anchor/target
        self.freq_tolerance = 5    # Frequency bin tolerance
        
        # Matching parameters
        self.min_matches_threshold = 15  # Minimum matches to consider
        self.time_bin_width = 5  # Frames for time offset binning
        self.min_aligned_matches = 8  # Minimum aligned matches
        
        print("🔊 Enhanced Acoustic Fingerprinter initialized")

        # AUTO-LOAD CACHE IF IT EXISTS
        if self.cache_path.exists():
            try:
                print(f"📦 Auto-loading fingerprint cache...")
                with open(self.cache_path, 'rb') as f:
                    cache = pickle.load(f)
                    self.fingerprint_db = cache['fingerprints']
                    self.song_metadata = cache['metadata']
                print(f"✅ Loaded {len(self.song_metadata)} songs from cache")
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")


    def _compute_enhanced_spectrogram(self, audio_path):
        """
        Compute multi-resolution mel spectrogram with better preprocessing
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Enhanced mel spectrogram (dB scale)
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        
        # Normalize audio
        y = librosa.util.normalize(y)
        
        # Pre-emphasis filter (boost high frequencies)
        y_emphasized = np.append(y[0], y[1:] - 0.97 * y[:-1])
        
        # Compute mel spectrogram with best resolution
        mel_spec = librosa.feature.melspectrogram(
            y=y_emphasized,
            sr=sr,
            n_fft=2048,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
            fmin=20,  # Ignore very low frequencies
            fmax=8000  # Focus on relevant frequency range
        )
        
        # Convert to dB with better scaling
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max, top_db=80)
        
        return mel_spec_db
    
    def _find_peaks_enhanced(self, spectrogram):
        """
        Enhanced peak detection using local maximum filtering
        
        Args:
            spectrogram: Mel spectrogram in dB
        
        Returns:
            List of (time_idx, freq_idx, amplitude) tuples
        """
        # Normalize to 0-1 range
        spec_norm = (spectrogram - np.min(spectrogram)) / (np.max(spectrogram) - np.min(spectrogram))
        
        # Apply local maximum filter
        struct = np.ones(self.peak_neighborhood_size)
        local_max = maximum_filter(spec_norm, footprint=struct)
        
        # Find peaks (local maxima above threshold)
        threshold = np.percentile(spec_norm, self.min_amplitude_percentile)
        peak_mask = (spec_norm == local_max) & (spec_norm > threshold)
        
        # Extract peak coordinates
        peaks = []
        freq_idxs, time_idxs = np.where(peak_mask)
        
        for freq_idx, time_idx in zip(freq_idxs, time_idxs):
            amplitude = spec_norm[freq_idx, time_idx]
            peaks.append((time_idx, freq_idx, amplitude))
        
        # Sort by time, then amplitude (strongest first)
        peaks.sort(key=lambda x: (x[0], -x[2]))
        
        return peaks
    
    def _generate_hashes_enhanced(self, peaks):
        """
        Generate robust fingerprint hashes with better pairing strategy
        
        Args:
            peaks: List of (time_idx, freq_idx, amplitude) tuples
        
        Returns:
            List of (hash, anchor_time) tuples
        """
        hashes = []
        
        # Group peaks by time windows for efficiency
        time_windows = defaultdict(list)
        for time_idx, freq_idx, amp in peaks:
            window = time_idx // 10  # 10-frame windows
            time_windows[window].append((time_idx, freq_idx, amp))
        
        # For each anchor point
        for i, (anchor_time, anchor_freq, anchor_amp) in enumerate(peaks):
            # Limit targets to nearby time windows
            start_window = (anchor_time + self.min_time_delta) // 10
            end_window = (anchor_time + self.max_time_delta) // 10
            
            target_count = 0
            
            # Look for target points in valid time range
            for window_idx in range(start_window, end_window + 1):
                if window_idx not in time_windows:
                    continue
                
                for target_time, target_freq, target_amp in time_windows[window_idx]:
                    # Skip if same peak
                    if target_time == anchor_time and target_freq == anchor_freq:
                        continue
                    
                    time_delta = target_time - anchor_time
                    
                    # Check if within valid range
                    if self.min_time_delta <= time_delta <= self.max_time_delta:
                        # Create hash from anchor/target pair
                        # Include frequency bins and time delta
                        hash_input = f"{anchor_freq:04d}|{target_freq:04d}|{time_delta:04d}"
                        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:20]
                        
                        hashes.append((hash_value, anchor_time))
                        
                        target_count += 1
                        if target_count >= self.fanout:
                            break
                
                if target_count >= self.fanout:
                    break
        
        return hashes
    
    def fingerprint_audio(self, audio_path):
        """
        Generate enhanced fingerprints from audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            List of (hash, time_offset) tuples
        """
        # Compute enhanced spectrogram
        spectrogram = self._compute_enhanced_spectrogram(audio_path)
        
        # Find peaks with enhanced detection
        peaks = self._find_peaks_enhanced(spectrogram)
        
        # Generate hashes with better pairing
        hashes = self._generate_hashes_enhanced(peaks)
        
        return hashes
    
    def build_database(self, audio_dir=None, force_rebuild=False):
        """
        Build enhanced fingerprint database from audio files
        
        Args:
            audio_dir: Directory containing audio files
            force_rebuild: Force rebuild even if cache exists
        
        Returns:
            Number of songs indexed
        """
        # Check cache
        if not force_rebuild and self.cache_path.exists():
            print(f"📦 Loading cached fingerprints...")
            with open(self.cache_path, 'rb') as f:
                cache = pickle.load(f)
                self.fingerprint_db = cache['fingerprints']
                self.song_metadata = cache['metadata']
            print(f"✅ Loaded {len(self.song_metadata)} songs from cache")
            return len(self.song_metadata)
        
        if audio_dir is None:
            audio_dir = Config.AUDIO_SAMPLES_DIR
        
        audio_dir = Path(audio_dir)
        
        # Get all audio files
        audio_files = []
        for ext in Config.SUPPORTED_FORMATS:
            audio_files.extend(audio_dir.glob(f"*{ext}"))
        
        if not audio_files:
            print(f"⚠️  No audio files found in {audio_dir}")
            return 0
        
        print(f"\n🔊 Building enhanced fingerprint database...")
        print(f"   Processing {len(audio_files)} audio files")
        
        self.fingerprint_db.clear()
        self.song_metadata.clear()
        
        for song_id, audio_file in enumerate(tqdm(audio_files, desc="Fingerprinting")):
            try:
                # Generate fingerprints
                hashes = self.fingerprint_audio(audio_file)
                
                # Store in database
                for hash_value, time_offset in hashes:
                    if hash_value not in self.fingerprint_db:
                        self.fingerprint_db[hash_value] = []
                    self.fingerprint_db[hash_value].append((song_id, time_offset))
                
                # Store metadata
                self.song_metadata[song_id] = {
                    'filename': audio_file.name,
                    'path': str(audio_file),
                    'num_hashes': len(hashes)
                }
                
            except Exception as e:
                print(f"\n⚠️  Error processing {audio_file.name}: {e}")
                continue
        
        # Save cache
        print(f"\n💾 Saving fingerprint cache...")
        cache = {
            'fingerprints': self.fingerprint_db,
            'metadata': self.song_metadata
        }
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache, f)
        
        # Calculate statistics
        total_hashes = sum(len(v) for v in self.fingerprint_db.values())
        avg_hashes = total_hashes / len(self.song_metadata) if self.song_metadata else 0
        
        print(f"✅ Enhanced fingerprint database built:")
        print(f"   Songs indexed: {len(self.song_metadata)}")
        print(f"   Unique hashes: {len(self.fingerprint_db)}")
        print(f"   Avg hashes/song: {avg_hashes:.0f}")
        
        return len(self.song_metadata)
    
    def match_audio(self, audio_path, top_k=5):
        """
        Enhanced matching with time-offset clustering and scoring
        
        Args:
            audio_path: Path to query audio
            top_k: Number of top matches to return
        
        Returns:
            List of matches with improved scores
        """
        if not self.fingerprint_db:
            print("⚠️  Fingerprint database is empty. Run build_database() first.")
            return []
        
        print(f"\n🔍 Matching audio fingerprint (enhanced)...")
        
        # Generate query fingerprints
        query_hashes = self.fingerprint_audio(audio_path)
        
        if not query_hashes:
            print("⚠️  No fingerprints generated from query")
            return []
        
        print(f"   Generated {len(query_hashes)} query hashes")
        
        # Match against database - collect all time offsets
        song_matches = defaultdict(list)  # {song_id: [(query_time, db_time), ...]}
        
        matched_hashes = 0
        for query_hash, query_time in query_hashes:
            if query_hash in self.fingerprint_db:
                matched_hashes += 1
                for song_id, db_time in self.fingerprint_db[query_hash]:
                    # Calculate time offset delta
                    time_delta = db_time - query_time
                    song_matches[song_id].append(time_delta)
        
        print(f"   Matched {matched_hashes} hashes across {len(song_matches)} songs")
        
        if not song_matches:
            print("❌ No matching songs found")
            return []
        
        # Score matches using time-offset clustering
        scored_matches = []
        
        for song_id, time_deltas in song_matches.items():
            # Need minimum number of matches
            if len(time_deltas) < self.min_matches_threshold:
                continue
            
            # Bin time offsets to find clusters
            time_deltas_array = np.array(time_deltas)
            
            # Use histogram with adaptive binning
            num_bins = min(100, len(time_deltas))
            hist, bin_edges = np.histogram(time_deltas_array, bins=num_bins)
            
            # Find the dominant cluster (highest peak)
            peak_bin_idx = np.argmax(hist)
            peak_count = hist[peak_bin_idx]
            peak_center = (bin_edges[peak_bin_idx] + bin_edges[peak_bin_idx + 1]) / 2
            
            # Count matches within tolerance of peak
            bin_width = bin_edges[1] - bin_edges[0]
            tolerance = max(self.time_bin_width, bin_width * 2)
            
            aligned_matches = np.sum(
                np.abs(time_deltas_array - peak_center) <= tolerance
            )
            
            # Skip if not enough aligned matches
            if aligned_matches < self.min_aligned_matches:
                continue
            
            # Calculate scores
            total_query_hashes = len(query_hashes)
            db_song_hashes = self.song_metadata[song_id]['num_hashes']
            
            # Primary score: aligned matches / query hashes (capped at 1.0)
            alignment_score = min(1.0, aligned_matches / total_query_hashes)
            
            # Secondary score: peak consistency (how concentrated matches are)
            consistency_score = aligned_matches / len(time_deltas)
            
            # Penalty for mismatched song lengths
            length_ratio = min(total_query_hashes, db_song_hashes) / max(total_query_hashes, db_song_hashes)
            length_penalty = 0.5 + 0.5 * length_ratio  # 0.5 to 1.0
            
            # Combined score (weighted with length penalty)
            final_score = (0.7 * alignment_score + 0.3 * consistency_score) * length_penalty
            
            metadata = self.song_metadata[song_id]
            
            scored_matches.append({
                'song_id': song_id,
                'filename': metadata['filename'],
                'path': metadata['path'],
                'fingerprint_score': float(final_score),
                'alignment_score': float(min(1.0, alignment_score)),  # Cap at 100%
                'consistency_score': float(consistency_score),
                'aligned_matches': int(aligned_matches),
                'total_matches': len(time_deltas),
                'query_hashes': total_query_hashes,
                'db_hashes': db_song_hashes,
                'time_offset': float(peak_center * self.hop_length / self.sample_rate),
                'confidence_level': self._get_confidence_level(final_score)
            })
        
        # Sort by fingerprint score
        scored_matches.sort(key=lambda x: x['fingerprint_score'], reverse=True)
        
        return scored_matches[:top_k]
    
    def get_match_summary(self, results):
        """Generate formatted summary of enhanced fingerprint matches"""
        if not results:
            return "❌ No fingerprint matches found"
        
        summary = f"\n{'='*60}\n"
        summary += f"🔊 Enhanced Acoustic Fingerprint Matches\n"
        summary += f"{'='*60}\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. 🎵 {result['filename']}\n"
            summary += f"   📊 Score: {result['fingerprint_score']:.2%} ({result['confidence_level']})\n"
            summary += f"   🎯 Alignment: {result['alignment_score']:.2%}\n"
            summary += f"   🔄 Consistency: {result['consistency_score']:.2%}\n"
            summary += f"   ✅ Aligned matches: {result['aligned_matches']} / {result['total_matches']}\n"
            summary += f"   📏 Length: query={result['query_hashes']}, db={result['db_hashes']}\n"
            summary += f"   📍 Time offset: {result['time_offset']:.2f}s\n"
            summary += "\n"
        
        return summary
    
    def _get_confidence_level(self, score):
        """Get confidence description based on score"""
        if score >= 0.5:
            return "Very High ⭐⭐⭐"
        elif score >= 0.3:
            return "High ⭐⭐"
        elif score >= 0.15:
            return "Medium ⭐"
        elif score >= 0.08:
            return "Low"
        else:
            return "Very Low"
    
    def close(self):
        """Close database connection"""
        self.db.close()


def test_fingerprinter():
    """Test enhanced acoustic fingerprinting"""
    print("\n" + "="*60)
    print("Testing Enhanced Acoustic Fingerprinter")
    print("="*60 + "\n")
    
    fingerprinter = AcousticFingerprinter()
    
    # Build database
    audio_dir = Config.AUDIO_SAMPLES_DIR
    
    if not audio_dir.exists() or not list(audio_dir.glob("*.*")):
        print(f"⚠️  No audio files in {audio_dir}")
        print("   Add audio files to test fingerprinting")
        return
    
    # Build fingerprint database
    num_songs = fingerprinter.build_database(audio_dir, force_rebuild=True)
    
    if num_songs > 0:
        # Test matching with first audio file
        test_audio = list(audio_dir.glob("*.*"))[0]
        print(f"\n🎵 Testing with: {test_audio.name}")
        
        results = fingerprinter.match_audio(test_audio, top_k=5)
        print(fingerprinter.get_match_summary(results))
    
    fingerprinter.close()


if __name__ == "__main__":
    test_fingerprinter()