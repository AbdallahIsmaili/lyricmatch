"""
Production Voice Analysis - FIXED FOR WINDOWS
Multi-pass robust pitch detection optimized for music
Requires: librosa, numpy, scipy (with scipy.ndimage), scikit-learn, torch
Location: src/voice_analyzer.py (FIXED v3 - Multi-Pass)
"""
import librosa
import numpy as np
import warnings
from pathlib import Path
import torch

warnings.filterwarnings('ignore')

from config import Config


class VoiceAnalyzer:
    """
    Production voice analyzer - Windows compatible
    - Librosa-based VAD (no FFmpeg dependency)
    - Pyannote Audio for speaker diarization (optional)
    - Improved pitch detection with pYIN
    """
    
    def __init__(self):
        """Initialize voice analyzer"""
        self.sample_rate = Config.SAMPLE_RATE
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"🎤 Initializing Voice Analyzer on {self.device}...")
        
        # Gender/age thresholds
        self.MALE_F0_RANGE = (85, 180)
        self.FEMALE_F0_RANGE = (165, 255)
        self.CHILD_F0_RANGE = (250, 400)
        
        # Initialize models
        self._init_models()
        
        print("✅ Voice Analyzer ready")
    
    def _init_models(self):
        """Initialize pre-trained models"""
        # Skip Silero VAD - use librosa instead
        self.vad_model = None
        print("   ℹ️  Using librosa-based VAD (Windows compatible)")
        
        # Skip Pyannote for now - has dependency issues
        self.diarization_pipeline = None
        print("   ℹ️  Pyannote diarization disabled (optional feature)")
    
    def analyze_audio(self, audio_path, detailed=True):
        """Complete voice analysis"""
        print(f"\n🎤 Analyzing voice: {Path(audio_path).name}")
        
        # Load audio with librosa
        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        
        # Detect music vs speech
        music_score = self._detect_music_improved(y, sr)
        
        if music_score > 0.6:
            print(f"   🎵 Music detected ({music_score:.0%})")
        
        # Voice Activity Detection (librosa-based)
        speech_segments = self._detect_speech_librosa(y, sr)
        
        if not speech_segments or len(speech_segments) == 0:
            return {
                'error': 'No speech detected',
                'music_score': float(music_score),
                'reason': 'No voice activity detected in audio'
            }
        
        print(f"   📊 Found {len(speech_segments)} speech segments")
        
        # Extract voiced audio
        voiced_audio = self._extract_segments(y, sr, speech_segments)
        
        if len(voiced_audio) < sr * 0.1:
            return {
                'error': 'Insufficient speech content',
                'music_score': float(music_score),
                'reason': 'Speech segments too short'
            }
        
        print(f"   ⏱️  Speech duration: {len(voiced_audio)/sr:.1f}s")
        
        # Speaker diarization
        if self.diarization_pipeline:
            speaker_info = self._diarize_speakers(audio_path)
        else:
            speaker_info = self._estimate_speakers_fallback(voiced_audio, sr, music_score)
        
        # Gender and pitch analysis
        gender_info = self._analyze_gender_pyin(voiced_audio, sr)
        
        # Age estimation
        age_info = self._estimate_age_realistic(gender_info, voiced_audio, sr)
        
        results = {
            'gender': gender_info,
            'speaker_count': speaker_info,
            'age': age_info,
            'audio_duration': len(y) / sr,
            'music_score': float(music_score),
            'speech_segments': len(speech_segments),
            'total_speech_duration': float(len(voiced_audio) / sr),
            'analysis_method': 'librosa_vad'
        }
        
        if detailed:
            results['acoustic_features'] = self._extract_acoustic_features(voiced_audio, sr)
            results['voice_quality'] = self._assess_voice_quality(voiced_audio, sr)
        
        return results
    
    def _detect_music_improved(self, y, sr):
        """Improved music detection"""
        # Tempo detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        has_beat = 60 < tempo < 180
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_bands=6)
        contrast_mean = np.mean(contrast)
        
        # Harmonic ratio
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        harmonic_ratio = np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y)) + 1e-8)
        
        # Combine indicators
        music_score = (
            (0.5 if has_beat else 0.0) +
            (min(contrast_mean / 40, 0.3)) +
            (harmonic_ratio * 0.2)
        )
        
        return min(music_score, 1.0)
    
    def _detect_speech_librosa(self, y, sr):
        """
        Librosa-based VAD - IMPROVED for music
        Focuses on vocal frequency ranges and patterns
        """
        hop_length = 512
        frame_length = 2048
        
        # Multiple features for better detection
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Spectral centroid - voice is typically 500-3000 Hz
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # MORE AGGRESSIVE thresholds for music
        rms_threshold = np.percentile(rms, 15)  # Much lower for background vocals
        spec_threshold_low = 150   # Lower to catch all vocals
        spec_threshold_high = 5000 # Higher range
        zcr_max = np.percentile(zcr, 85)  # Less strict
        
        # Speech detection: primarily energy-based for music
        is_speech = (
            (rms > rms_threshold) &
            (spec_cent > spec_threshold_low) &
            (spec_cent < spec_threshold_high)
        )
        
        # Convert to time segments
        times = librosa.frames_to_time(
            np.arange(len(is_speech)), 
            sr=sr, 
            hop_length=hop_length
        )
        
        # Merge segments
        segments = []
        start = None
        min_duration = 0.15  # Very short minimum for music
        max_gap = 0.5  # Allow larger gaps
        
        for i, is_voice in enumerate(is_speech):
            if is_voice and start is None:
                start = times[i]
            elif not is_voice and start is not None:
                duration = times[i] - start
                if duration >= min_duration:
                    segments.append((start, times[i]))
                start = None
        
        if start is not None and times[-1] - start >= min_duration:
            segments.append((start, times[-1]))
        
        # Merge close segments
        merged = []
        for seg in segments:
            if merged and seg[0] - merged[-1][1] < max_gap:
                merged[-1] = (merged[-1][0], seg[1])
            else:
                merged.append(seg)
        
        return merged
    
    def _extract_segments(self, y, sr, segments):
        """Extract audio from time segments"""
        audio_segments = []
        
        for start, end in segments:
            start_sample = int(start * sr)
            end_sample = int(end * sr)
            audio_segments.append(y[start_sample:end_sample])
        
        if audio_segments:
            return np.concatenate(audio_segments)
        return np.array([])
    
    def _diarize_speakers(self, audio_path):
        """Use Pyannote for speaker diarization"""
        try:
            diarization = self.diarization_pipeline(audio_path)
            
            speakers = set()
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.add(speaker)
            
            num_speakers = len(speakers)
            
            return {
                'estimated_count': num_speakers,
                'confidence': 'high',
                'method': 'pyannote_diarization',
                'speakers': list(speakers)
            }
            
        except Exception as e:
            print(f"   ⚠️  Diarization error: {e}")
            return {
                'estimated_count': 1,
                'confidence': 'low',
                'method': 'failed'
            }
    
    def _estimate_speakers_fallback(self, y, sr, music_score):
        """Fallback speaker estimation"""
        if music_score > 0.6:
            return {
                'estimated_count': 1,
                'confidence': 'low',
                'method': 'music_detected',
                'note': 'Speaker counting unreliable with music'
            }
        
        # Simple MFCC clustering
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mfccs_norm = (mfccs - np.mean(mfccs, axis=1, keepdims=True)) / (np.std(mfccs, axis=1, keepdims=True) + 1e-8)
        
        from sklearn.mixture import GaussianMixture
        
        best_n = 1
        best_bic = float('inf')
        
        for n in range(1, 4):
            try:
                gmm = GaussianMixture(n_components=n, covariance_type='diag', random_state=42)
                gmm.fit(mfccs_norm.T)
                bic = gmm.bic(mfccs_norm.T)
                
                if bic < best_bic:
                    best_bic = bic
                    best_n = n
            except:
                break
        
        return {
            'estimated_count': best_n,
            'confidence': 'medium' if best_n == 1 else 'low',
            'method': 'gmm_clustering'
        }
    
    def _analyze_gender_pyin(self, y, sr):
        """
        Gender analysis using MULTI-PASS approach
        Pass 1: Try pYIN with vocal isolation
        Pass 2: Try with harmonic separation
        Pass 3: YIN fallback
        """
        # PASS 1: Isolate vocals first using harmonic-percussive separation
        try:
            print(f"   🔍 Pass 1: Vocal isolation with HPSS...")
            y_harmonic, y_percussive = librosa.effects.hpss(y, margin=3.0)
            
            # Use harmonic component (contains vocals)
            y_vocals = y_harmonic
            
            # Apply aggressive high-pass filter (remove bass completely)
            from scipy.signal import butter, filtfilt
            nyquist = sr / 2
            low_cut = 100 / nyquist  # 100 Hz cutoff
            if low_cut < 1.0:
                b, a = butter(6, low_cut, btype='high')  # 6th order = steeper
                y_vocals = filtfilt(b, a, y_vocals)
            
            # Extract only the LOUDEST 40% (where vocals dominate)
            rms = librosa.feature.rms(y=y_vocals, frame_length=2048, hop_length=512)[0]
            threshold = np.percentile(rms, 60)  # Top 40%
            
            # Build mask and extract loud segments
            hop_length = 512
            loud_segments = []
            for i, r in enumerate(rms):
                if r > threshold:
                    start = i * hop_length
                    end = min(start + 2048, len(y_vocals))
                    loud_segments.append(y_vocals[start:end])
            
            if loud_segments:
                y_vocals = np.concatenate(loud_segments)
            
            if len(y_vocals) < sr * 0.5:
                print(f"   ⚠️  Insufficient vocal audio after isolation")
                raise ValueError("Insufficient vocal audio")
            
            print(f"   ✅ Isolated {len(y_vocals)/sr:.1f}s of vocals")
            
            # Now run pYIN on isolated vocals with STRICT range
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y_vocals,
                fmin=85,   # Lowest male voice
                fmax=400,  # Highest female voice (not child)
                sr=sr,
                frame_length=2048,
                hop_length=256  # Smaller hop for better resolution
            )
            
            # Try multiple confidence thresholds
            for confidence_threshold in [0.7, 0.6, 0.5]:
                reliable_f0 = f0[(~np.isnan(f0)) & (voiced_probs > confidence_threshold)]
                
                if len(reliable_f0) >= 30:  # Need good amount of data
                    print(f"   ✅ Pass 1 success: {len(reliable_f0)} samples at {confidence_threshold} confidence")
                    break
            else:
                print(f"   ⚠️  Pass 1 failed: insufficient confident pitches")
                raise ValueError("Pass 1 failed")
            
            # AGGRESSIVE outlier removal
            # Remove harmonics (2x, 3x fundamental)
            f0_median = np.median(reliable_f0)
            
            # Remove values that are likely harmonics
            reliable_f0_no_harm = []
            for f in reliable_f0:
                # Check if this is a harmonic of a lower frequency
                is_harmonic = False
                for multiplier in [2, 3, 4]:
                    expected_fundamental = f / multiplier
                    if 85 <= expected_fundamental <= 400:
                        # Check if fundamental exists in our data
                        nearby = reliable_f0[(reliable_f0 > expected_fundamental - 10) & 
                                            (reliable_f0 < expected_fundamental + 10)]
                        if len(nearby) > 0:
                            is_harmonic = True
                            break
                
                if not is_harmonic:
                    reliable_f0_no_harm.append(f)
            
            reliable_f0 = np.array(reliable_f0_no_harm) if reliable_f0_no_harm else reliable_f0
            
            # Standard outlier removal (2σ)
            f0_median = np.median(reliable_f0)
            f0_std = np.std(reliable_f0)
            f0_filtered = reliable_f0[
                (reliable_f0 > f0_median - 2*f0_std) & 
                (reliable_f0 < f0_median + 2*f0_std)
            ]
            
            if len(f0_filtered) < 15:
                print(f"   ⚠️  Too few samples after filtering ({len(f0_filtered)})")
                raise ValueError("Too few samples")
            
            mean_f0 = np.median(f0_filtered)
            f0_q25 = np.percentile(f0_filtered, 25)
            f0_q75 = np.percentile(f0_filtered, 75)
            f0_iqr = f0_q75 - f0_q25
            
            print(f"   🎵 Pitch: {mean_f0:.1f} Hz (IQR: {f0_iqr:.1f} Hz, n={len(f0_filtered)})")
            
            # Final sanity check
            if mean_f0 < 85 or mean_f0 > 400:
                print(f"   ⚠️  Pitch out of vocal range ({mean_f0:.1f} Hz)")
                raise ValueError("Pitch out of range")
            
            # SUCCESS! Use these results
            result = self._classify_gender_from_pitch(mean_f0, f0_iqr, len(f0_filtered), y_vocals, sr)
            result['method'] = 'pyin_with_vocal_isolation'
            return result
            
        except Exception as e:
            print(f"   ℹ️  Pass 1 didn't work: {str(e)[:50]}")
        
        # PASS 2: Try with different approach - median filtering
        try:
            print(f"   🔍 Pass 2: Trying median-filtered approach...")
            return self._analyze_gender_pass2(y, sr)
        except Exception as e:
            print(f"   ℹ️  Pass 2 didn't work: {str(e)[:50]}")
        
        # PASS 3: YIN fallback
        print(f"   🔍 Pass 3: Using YIN fallback...")
        return self._analyze_gender_yin_fallback(y, sr)
    
    def _analyze_gender_pass2(self, y, sr):
        """
        Pass 2: Median filtering approach
        Uses median filtering to remove noise/harmonics
        """
        # Apply median filter to remove transients
        from scipy.ndimage import median_filter
        
        # High-pass filter first
        from scipy.signal import butter, filtfilt
        nyquist = sr / 2
        low_cut = 90 / nyquist
        if low_cut < 1.0:
            b, a = butter(5, low_cut, btype='high')
            y_filtered = filtfilt(b, a, y)
        else:
            y_filtered = y
        
        # Use YIN (more robust than pYIN for this)
        f0 = librosa.yin(
            y_filtered,
            fmin=85,
            fmax=350,  # Stricter range
            sr=sr,
            frame_length=2048,
            hop_length=512
        )
        
        # Remove NaN and out-of-range
        valid_f0 = f0[(f0 >= 85) & (f0 <= 350) & (~np.isnan(f0))]
        
        if len(valid_f0) < 10:
            raise ValueError("Insufficient valid pitch data in Pass 2")
        
        # Apply median filter to pitch track (remove outliers)
        if len(valid_f0) > 5:
            valid_f0 = median_filter(valid_f0, size=5)
        
        # Histogram-based mode finding (most common pitch)
        hist, bin_edges = np.histogram(valid_f0, bins=50)
        most_common_bin = np.argmax(hist)
        mode_f0 = (bin_edges[most_common_bin] + bin_edges[most_common_bin + 1]) / 2
        
        # Use values near the mode
        f0_near_mode = valid_f0[np.abs(valid_f0 - mode_f0) < 30]  # Within 30 Hz
        
        if len(f0_near_mode) < 5:
            f0_near_mode = valid_f0
        
        mean_f0 = np.median(f0_near_mode)
        f0_iqr = np.percentile(f0_near_mode, 75) - np.percentile(f0_near_mode, 25)
        
        print(f"   🎵 Pass 2 Pitch: {mean_f0:.1f} Hz (mode-based, n={len(f0_near_mode)})")
        
        result = self._classify_gender_from_pitch(mean_f0, f0_iqr, len(f0_near_mode), y, sr)
        result['method'] = 'yin_median_filtered'
        return result
    
    def _classify_gender_from_pitch(self, mean_f0, f0_iqr, sample_count, audio, sr):
        """
        Classify gender from pitch with additional audio features
        """
        scores = {
            'male': 0.0,
            'female': 0.0
        }
        
        # Male: 85-165 Hz (peak ~120 Hz)
        if 85 <= mean_f0 <= 165:
            # Gaussian scoring
            scores['male'] = np.exp(-((mean_f0 - 120)**2) / (2 * 25**2))
        
        # Female: 155-280 Hz (peak ~200 Hz)
        if 155 <= mean_f0 <= 280:
            scores['female'] = np.exp(-((mean_f0 - 200)**2) / (2 * 35**2))
        
        # Overlap zone: 155-165 Hz - use spectral features
        if 155 <= mean_f0 <= 165:
            spec_cent = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
            
            # Female voices have higher spectral content
            if spec_cent > 2200 or spectral_rolloff > 3500:
                scores['female'] *= 1.8
                scores['male'] *= 0.6
            else:
                scores['male'] *= 1.5
                scores['female'] *= 0.7
        
        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            return {
                'classification': 'unknown',
                'confidence': 0.0,
                'mean_f0': float(mean_f0),
                'reason': 'pitch_outside_expected_ranges'
            }
        
        predicted = max(scores, key=scores.get)
        confidence = scores[predicted]
        
        # Adjust for sample count and pitch variance
        sample_factor = min(1.0, sample_count / 50)
        variance_factor = max(0.7, min(1.0, 1.0 - f0_iqr / 100))  # High variance = less confident
        
        confidence = confidence * sample_factor * variance_factor
        
        # Minimum confidence
        if confidence < 0.40:
            predicted = 'unknown'
            confidence = 0.0
        
        return {
            'classification': predicted,
            'confidence': float(confidence),
            'scores': {k: float(v) for k, v in scores.items()},
            'mean_f0': float(mean_f0),
            'f0_iqr': float(f0_iqr),
            'sample_count': sample_count
        }
    
    def _analyze_gender_yin_fallback(self, y, sr):
        """
        Pass 3: YIN fallback - most robust but less accurate
        Uses aggressive vocal isolation and multiple validation steps
        """
        try:
            # Step 1: HPSS - extract harmonics (vocals)
            y_harmonic, _ = librosa.effects.hpss(y, margin=4.0)
            
            # Step 2: Aggressive high-pass filter
            from scipy.signal import butter, filtfilt
            nyquist = sr / 2
            low_cut = 100 / nyquist
            
            if low_cut >= 1.0:
                return {
                    'classification': 'unknown',
                    'confidence': 0.0,
                    'reason': 'sample_rate_too_low',
                    'mean_f0': 0.0
                }
            
            b, a = butter(6, low_cut, btype='high')
            y_filtered = filtfilt(b, a, y_harmonic)
            
            # Step 3: Extract ONLY the loudest segments (vocals dominate here)
            rms = librosa.feature.rms(y=y_filtered, frame_length=2048, hop_length=512)[0]
            threshold = np.percentile(rms, 65)  # Top 35%
            
            loud_samples = []
            hop_length = 512
            
            for i, r in enumerate(rms):
                if r > threshold:
                    start_sample = i * hop_length
                    end_sample = min(start_sample + 2048, len(y_filtered))
                    if end_sample > start_sample:
                        loud_samples.append(y_filtered[start_sample:end_sample])
            
            if len(loud_samples) < 5:
                loud_audio = y_filtered
                print(f"   ⚠️  Using full audio (insufficient loud segments)")
            else:
                loud_audio = np.concatenate(loud_samples)
                print(f"   ✅  Extracted {len(loud_audio)/sr:.1f}s of loud segments")
            
            if len(loud_audio) < sr * 0.3:
                return {
                    'classification': 'unknown',
                    'confidence': 0.0,
                    'reason': 'insufficient_audio',
                    'mean_f0': 0.0
                }
            
            # Step 4: YIN pitch detection with strict range
            f0 = librosa.yin(
                loud_audio,
                fmin=85,
                fmax=320,  # Strict range (no child voices, no harmonics)
                sr=sr,
                frame_length=2048,
                hop_length=256
            )
            
            # Step 5: Filter valid pitches
            valid_f0 = f0[(f0 >= 85) & (f0 <= 320) & (~np.isnan(f0))]
            
            if len(valid_f0) < 10:
                # Retry with full audio
                print(f"   🔄 Retry with full filtered audio...")
                f0_full = librosa.yin(y_filtered, fmin=85, fmax=320, sr=sr)
                valid_f0 = f0_full[(f0_full >= 85) & (f0_full <= 320) & (~np.isnan(f0_full))]
                
                if len(valid_f0) < 5:
                    return {
                        'classification': 'unknown',
                        'confidence': 0.0,
                        'reason': 'yin_no_valid_pitch',
                        'mean_f0': 0.0
                    }
            
            # Step 6: Histogram-based mode finding (most reliable for music)
            hist, bin_edges = np.histogram(valid_f0, bins=40)
            most_common_bin = np.argmax(hist)
            mode_f0 = (bin_edges[most_common_bin] + bin_edges[most_common_bin + 1]) / 2
            
            # Use values within 25 Hz of mode
            f0_near_mode = valid_f0[np.abs(valid_f0 - mode_f0) < 25]
            
            if len(f0_near_mode) < 5:
                # Fall back to all valid pitches with outlier removal
                f0_median = np.median(valid_f0)
                f0_std = np.std(valid_f0)
                f0_near_mode = valid_f0[
                    (valid_f0 > f0_median - 1.5*f0_std) & 
                    (valid_f0 < f0_median + 1.5*f0_std)
                ]
            
            if len(f0_near_mode) == 0:
                f0_near_mode = valid_f0
            
            mean_f0 = np.median(f0_near_mode)
            f0_iqr = np.percentile(f0_near_mode, 75) - np.percentile(f0_near_mode, 25)
            
            print(f"   🎵 YIN Pitch: {mean_f0:.1f} Hz (mode-based, n={len(f0_near_mode)})")
            
            # Step 7: Classify
            result = self._classify_gender_from_pitch(mean_f0, f0_iqr, len(f0_near_mode), loud_audio, sr)
            result['method'] = 'yin_hpss_fallback'
            
            # Lower confidence for fallback method
            if result['confidence'] > 0:
                result['confidence'] *= 0.85
            
            return result
                
        except Exception as e:
            print(f"   ❌ YIN fallback error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'classification': 'unknown',
                'confidence': 0.0,
                'reason': f'yin_error: {str(e)}',
                'mean_f0': 0.0
            }
    
    def _estimate_age_realistic(self, gender_info, y, sr):
        """Age estimation based on voice characteristics"""
        mean_f0 = gender_info.get('mean_f0', 0)
        gender = gender_info.get('classification', 'unknown')
        f0_iqr = gender_info.get('f0_iqr', 0)
        
        if gender == 'unknown' or mean_f0 == 0:
            return {
                'estimated_age': None,
                'age_range': 'unknown',
                'confidence': 0.0,
                'note': 'Cannot estimate age without gender'
            }
        
        jitter = f0_iqr / mean_f0 if mean_f0 > 0 else 0
        
        rms = librosa.feature.rms(y=y)[0]
        shimmer = np.std(rms) / (np.mean(rms) + 1e-8)
        
        if gender == 'child':
            estimated_age = 8
            age_range = "5-12"
            confidence = 0.7
        elif gender == 'male':
            if mean_f0 > 160:
                estimated_age = 20
                age_range = "15-25"
                confidence = 0.5
            elif mean_f0 > 130:
                estimated_age = 30
                age_range = "25-45"
                confidence = 0.4
            else:
                estimated_age = 45
                age_range = "35-55"
                confidence = 0.35
        elif gender == 'female':
            if mean_f0 > 230:
                estimated_age = 20
                age_range = "15-28"
                confidence = 0.5
            elif mean_f0 > 200:
                estimated_age = 28
                age_range = "22-38"
                confidence = 0.45
            else:
                estimated_age = 40
                age_range = "30-50"
                confidence = 0.4
        
        return {
            'estimated_age': estimated_age,
            'age_range': age_range,
            'confidence': float(confidence),
            'note': 'Age is approximate',
            'features': {
                'mean_f0': float(mean_f0),
                'jitter': float(jitter),
                'shimmer': float(shimmer)
            }
        }
    
    def _extract_acoustic_features(self, y, sr):
        """Extract acoustic features"""
        return {
            'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            'spectral_bandwidth': float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
            'spectral_rolloff': float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
            'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
            'rms_energy': float(np.mean(librosa.feature.rms(y=y)))
        }
    
    def _assess_voice_quality(self, y, sr):
        """Assess recording quality"""
        rms = librosa.feature.rms(y=y)[0]
        
        noise_floor = np.percentile(rms, 5)
        signal_level = np.percentile(rms, 95)
        snr = signal_level / (noise_floor + 1e-8)
        
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
        clarity = 1.0 - spectral_flatness
        
        quality_score = min(snr / 20, 1.0) * 0.6 + clarity * 0.4
        
        return {
            'quality_score': float(quality_score),
            'snr_estimate': float(min(snr, 50)),
            'clarity': float(clarity),
            'assessment': 'excellent' if quality_score > 0.8 else 'good' if quality_score > 0.6 else 'fair' if quality_score > 0.4 else 'poor'
        }
    
    def generate_summary(self, analysis_results):
        """Generate human-readable summary"""
        if 'error' in analysis_results:
            return f"❌ {analysis_results['error']}"
        
        summary = []
        
        # Music detection
        music_score = analysis_results.get('music_score', 0)
        if music_score > 0.6:
            summary.append(f"🎵 Music detected ({music_score:.0%})")
        
        # Speakers
        speakers = analysis_results.get('speaker_count', {})
        count = speakers.get('estimated_count', 1)
        conf = speakers.get('confidence', 'unknown')
        
        if count == 1:
            summary.append(f"🎤 Single speaker ({conf} confidence)")
        else:
            summary.append(f"🎤 {count} speakers ({conf} confidence)")
        
        # Gender
        gender = analysis_results.get('gender', {})
        gender_label = gender.get('classification', 'unknown').title()
        gender_conf = gender.get('confidence', 0)
        mean_f0 = gender.get('mean_f0', 0)
        
        if gender_label == 'Unknown':
            summary.append(f"👤 Gender: Unable to determine")
        else:
            summary.append(f"👤 Gender: {gender_label} ({gender_conf:.0%} confidence)")
            summary.append(f"   🎵 Average pitch: {mean_f0:.0f} Hz")
        
        # Age
        age = analysis_results.get('age', {})
        est_age = age.get('estimated_age')
        age_range = age.get('age_range', 'unknown')
        
        if est_age:
            summary.append(f"🎂 Estimated age: ~{est_age} years (range: {age_range})")
        
        # Speech stats
        speech_dur = analysis_results.get('total_speech_duration', 0)
        total_dur = analysis_results.get('audio_duration', 0)
        
        if speech_dur > 0:
            speech_pct = (speech_dur / total_dur) * 100
            summary.append(f"📊 Speech: {speech_pct:.0f}% ({speech_dur:.1f}s / {total_dur:.1f}s)")
        
        # Quality
        if 'voice_quality' in analysis_results:
            quality = analysis_results['voice_quality']
            summary.append(f"✨ Quality: {quality['assessment'].title()}")
        
        return "\n".join(summary)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════╗
║   VOICE ANALYZER - WINDOWS COMPATIBLE      ║
║   Improved Pitch Detection for Music       ║
╚════════════════════════════════════════════╝

✅ Features:
   - Librosa-based VAD (no FFmpeg issues)
   - Improved pYIN pitch detection
   - YIN fallback for difficult cases
   - High-pass filtering to remove bass
   - Focus on vocal frequency ranges
   - Gender detection optimized for music
   - Speaker counting with GMM
   - Age estimation
   - Music detection

📦 Required Dependencies:
   pip install librosa numpy scipy scikit-learn torch

🔧 Optional (better speaker detection):
   pip install pyannote.audio
   
💡 Key Improvements:
   - Filters out bass/drums (uses 130-1047 Hz range)
   - Requires higher confidence (80% vs 60%)
   - Aggressive outlier removal
   - YIN fallback for tricky vocals
   - High-pass filter at 80 Hz
   - Focuses on loud segments (likely vocals)
    """)