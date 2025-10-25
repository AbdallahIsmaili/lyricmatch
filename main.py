"""
Main pipeline for WaveSeek - Audio to Song Recognition
Enhanced with neural embeddings support
"""
import argparse
from pathlib import Path
import sys

from config import Config
from src.audio_processor import AudioProcessor
from src.transcriber import Transcriber
from src.matcher import LyricsMatcher  # TF-IDF
from src.neural_matcher import NeuralLyricsMatcher  # Neural


class WaveSeek:
    """Main WaveSeek pipeline with multiple matching engines"""
    
    def __init__(self, whisper_model=None, language=None, matching_engine=None):
        """
        Initialize WaveSeek pipeline
        
        Args:
            whisper_model: Whisper model size to use
            language: Language code or None for auto-detection
            matching_engine: 'tfidf', 'neural', or 'hybrid'
        """
        print("\n╔" + "="*58 + "╗")
        print("║" + " "*20 + "WAVESEEK" + " "*28 + "║")
        print("║" + " "*12 + "Audio-to-Lyrics Song Recognition" + " "*13 + "║")
        print("╚" + "="*58 + "╝\n")
        
        print("🔄 Initializing components...\n")
        
        # Store settings
        self.language = language
        self.matching_engine = matching_engine or Config.MATCHING_ENGINE
        
        # Initialize audio processing and transcription
        self.audio_processor = AudioProcessor()
        self.transcriber = Transcriber(model_name=whisper_model or Config.WHISPER_MODEL)
        
        # Initialize matcher based on engine
        self.matcher = self._init_matcher()
        
        lang_msg = "Auto-detect" if self.language is None else self.language
        print(f"🌐 Language mode: {lang_msg}")
        print(f"🔍 Matching engine: {self.matching_engine.upper()}")
        print("\n✅ All components initialized successfully!\n")
    
    def _init_matcher(self):
        """Initialize the appropriate matching engine"""
        if self.matching_engine == "neural":
            print(f"🧠 Loading Neural Matcher (SBERT: {Config.SBERT_MODEL})...")
            return NeuralLyricsMatcher(model_name=Config.SBERT_MODEL)
        elif self.matching_engine == "tfidf":
            print("📊 Loading TF-IDF Matcher...")
            return LyricsMatcher()
        elif self.matching_engine == "hybrid":
            print(f"🔄 Loading Hybrid Matcher (Neural + Fuzzy)...")
            return NeuralLyricsMatcher(model_name=Config.SBERT_MODEL)
        else:
            print(f"⚠️  Unknown engine '{self.matching_engine}', defaulting to neural")
            return NeuralLyricsMatcher(model_name=Config.SBERT_MODEL)
    
    def identify_song(self, audio_path, preprocess=True, top_k=None, verbose=True, language=None):
        """
        Complete pipeline: Audio → Transcription → Matching
        
        Args:
            audio_path: Path to audio file
            preprocess: Apply audio preprocessing
            top_k: Number of top matches to return
            verbose: Print detailed information
            language: Language code or None for auto-detection
        
        Returns:
            List of matching songs
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Use provided language or fall back to instance language
        lang = language if language is not None else self.language
        
        print("="*60)
        print(f"🎵 Processing: {audio_path.name}")
        print("="*60)
        
        # Step 1: Audio Processing
        if verbose:
            print("\n📊 Step 1: Audio Processing")
            print("-"*60)
        
        if preprocess:
            audio, sr = self.audio_processor.preprocess_audio(audio_path)
        else:
            audio, sr = self.audio_processor.load_audio(audio_path)
        
        # Step 2: Transcription
        if verbose:
            print("\n🎤 Step 2: Speech-to-Text Transcription")
            if lang is None:
                print("   🌐 Auto-detecting language...")
            else:
                print(f"   🌐 Using language: {lang}")
            print("-"*60)
        
        transcription = self.transcriber.transcribe(str(audio_path), language=lang)
        
        if not transcription['text']:
            print("\n⚠️  No text was transcribed from the audio")
            return []
        
        # Display language info
        if verbose:
            lang_name = Config.SUPPORTED_LANGUAGES.get(
                transcription['language'], 
                transcription['language']
            )
            print(f"\n🌐 Detected Language: {lang_name} ({transcription['language']})")
            print(f"   Confidence: {transcription.get('language_probability', 0):.2%}")
        
        # Step 3: Matching with selected engine
        if verbose:
            print(f"\n🔍 Step 3: Lyrics Matching ({self.matching_engine.upper()})")
            print("-"*60)
        
        results = self.matcher.match_with_details(
            transcription['text'],
            top_k=top_k or Config.TOP_K_RESULTS
        )
        
        # Display results
        if verbose:
            print(self.matcher.get_match_summary(results))
        
        # Add transcription info to results
        for result in results:
            result['transcription'] = transcription['text']
            result['transcription_language'] = transcription['language']
            result['language_confidence'] = transcription.get('language_probability', 0)
            result['matching_engine'] = self.matching_engine
        
        return results
    
    def batch_identify(self, audio_dir, output_file=None, language=None):
        """
        Process multiple audio files
        
        Args:
            audio_dir: Directory containing audio files
            output_file: Optional output CSV file for results
            language: Language code or None for auto-detection
        
        Returns:
            Dictionary of results
        """
        audio_dir = Path(audio_dir)
        
        if not audio_dir.exists():
            raise FileNotFoundError(f"Directory not found: {audio_dir}")
        
        # Find all audio files
        audio_files = []
        for ext in Config.SUPPORTED_FORMATS:
            audio_files.extend(audio_dir.glob(f"*{ext}"))
        
        if not audio_files:
            print(f"⚠️  No audio files found in: {audio_dir}")
            return {}
        
        print(f"\n📂 Found {len(audio_files)} audio file(s)")
        print("="*60)
        
        all_results = {}
        
        for audio_file in audio_files:
            try:
                results = self.identify_song(
                    audio_file, 
                    verbose=False,
                    language=language
                )
                all_results[audio_file.name] = results
                
                if results:
                    top_match = results[0]
                    lang = top_match.get('transcription_language', '?')
                    engine = top_match.get('matching_engine', '?')
                    print(f"✅ {audio_file.name} [{lang}] [{engine}]")
                    print(f"   → {top_match['artist']} - {top_match['title']} "
                          f"({top_match['final_score']:.2%})")
                else:
                    print(f"❌ {audio_file.name} - No match found")
                
            except Exception as e:
                print(f"⚠️  {audio_file.name} - Error: {e}")
                all_results[audio_file.name] = []
        
        # Save results if output file specified
        if output_file:
            self._save_results(all_results, output_file)
        
        return all_results
    
    def _save_results(self, results, output_file):
        """Save results to CSV"""
        import pandas as pd
        
        rows = []
        for filename, matches in results.items():
            if matches:
                for i, match in enumerate(matches):
                    rows.append({
                        'filename': filename,
                        'rank': i + 1,
                        'artist': match['artist'],
                        'title': match['title'],
                        'album': match.get('album'),
                        'year': match.get('year'),
                        'score': match['final_score'],
                        'engine': match.get('matching_engine', ''),
                        'language': match.get('transcription_language', ''),
                        'lang_confidence': match.get('language_confidence', 0),
                        'transcription': match.get('transcription', '')
                    })
            else:
                rows.append({
                    'filename': filename,
                    'rank': 0,
                    'artist': None,
                    'title': 'No match',
                    'album': None,
                    'year': None,
                    'score': 0,
                    'engine': '',
                    'language': '',
                    'lang_confidence': 0,
                    'transcription': ''
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
    
    def close(self):
        """Close all connections"""
        self.matcher.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='WaveSeek - Identify songs from audio clips (Neural Embeddings)',
        epilog='Examples:\n'
               '  %(prog)s song.wav                      # Use default engine\n'
               '  %(prog)s song.wav -e neural           # Neural embeddings\n'
               '  %(prog)s song.wav -e tfidf            # TF-IDF matching\n'
               '  %(prog)s song.wav -e hybrid           # Hybrid approach\n'
               '  %(prog)s song.wav -l ko               # Force Korean\n'
               '  %(prog)s audio_folder/ -b             # Batch process\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'audio_path',
        type=str,
        help='Path to audio file or directory'
    )
    
    parser.add_argument(
        '-m', '--model',
        type=str,
        default=Config.WHISPER_MODEL,
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )
    
    parser.add_argument(
        '-e', '--engine',
        type=str,
        default=Config.MATCHING_ENGINE,
        choices=['tfidf', 'neural', 'hybrid'],
        help='Matching engine (default: neural)'
    )
    
    parser.add_argument(
        '-s', '--sbert-model',
        type=str,
        default=Config.SBERT_MODEL,
        help='SBERT model name (default: all-MiniLM-L6-v2)'
    )
    
    parser.add_argument(
        '-l', '--language',
        type=str,
        default=None,
        help='Language code (e.g., en, ko, ja) or "none" for auto-detect'
    )
    
    parser.add_argument(
        '-k', '--top-k',
        type=int,
        default=Config.TOP_K_RESULTS,
        help='Number of top matches to return (default: 5)'
    )
    
    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='Process all audio files in directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output CSV file for batch results'
    )
    
    parser.add_argument(
        '--no-preprocess',
        action='store_true',
        help='Skip audio preprocessing'
    )
    
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List available SBERT models and exit'
    )
    
    parser.add_argument(
        '--rebuild-embeddings',
        action='store_true',
        help='Force rebuild of neural embeddings cache'
    )
    
    args = parser.parse_args()
    
    # Handle list models
    if args.list_models:
        Config.list_sbert_models()
        return 0
    
    # Handle language parameter
    language = args.language
    if language and language.lower() in ['none', 'auto', 'detect']:
        language = None
    
    # Update config if custom SBERT model specified
    if args.sbert_model != Config.SBERT_MODEL:
        Config.set_sbert_model(args.sbert_model)
    
    try:
        # Initialize WaveSeek
        waveseek = WaveSeek(
            whisper_model=args.model,
            language=language,
            matching_engine=args.engine
        )
        
        # Rebuild embeddings if requested
        if args.rebuild_embeddings and isinstance(waveseek.matcher, NeuralLyricsMatcher):
            print("\n🔄 Rebuilding neural embeddings...")
            waveseek.matcher.rebuild_embeddings()
        
        # Process audio
        if args.batch:
            results = waveseek.batch_identify(
                args.audio_path, 
                args.output,
                language=language
            )
        else:
            results = waveseek.identify_song(
                args.audio_path,
                preprocess=not args.no_preprocess,
                top_k=args.top_k,
                language=language
            )
        
        waveseek.close()
        
        # Return appropriate exit code
        if args.batch:
            return 0 if any(results.values()) else 1
        else:
            return 0 if results else 1
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())