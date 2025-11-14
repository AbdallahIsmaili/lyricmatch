"""
Fixed Test Script for Voice Analyzer
Handles None values and provides better error reporting
Location: tests/test_voice_analyzer.py (FIXED)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.voice_analyzer import VoiceAnalyzer
import json


def test_analyzer():
    """Test the voice analyzer with your files"""
    print("\n" + "="*70)
    print("  TESTING VOICE ANALYZER (WINDOWS COMPATIBLE)")
    print("="*70 + "\n")
    
    # Initialize
    try:
        analyzer = VoiceAnalyzer()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test files
    test_files = [
        {
            'path': 'test.wav',
            'expected': {
                'artist': 'Billie Eilish',
                'song': 'Bad Guy',
                'gender': 'female',
                'speakers': 1
            }
        },
        {
            'path': 'Khalid_-_Better_Official_Video.wav',
            'expected': {
                'artist': 'Khalid',
                'gender': 'male',
                'speakers': 1
            }
        },
        {
            'path': 'Ava_Max_Kings_&_Queens.mp3',
            'expected': {
                'artist': 'Ava Max',
                'gender': 'female',
                'speakers': 1
            }
        },
        {
            'path': 'Dua_Lipa_-_New_Rules_Official_Music_Video.wav',
            'expected': {
                'artist': 'Dua Lipa',
                'gender': 'female',
                'speakers': 1
            }
        },
        {
            'path': 'Charlie_Puth_-_We_Don_t_Talk_Anymore_feat._Selena_Gomez_Official_Video.wav',
            'expected': {
                'artist': 'Charlie Puth ft. Selena Gomez',
                'gender': 'both',
                'speakers': 2
            }
        },
        {
            'path': 'man_voice.mp3',
            'expected': {
                'artist': 'A man voice',
                'song': 'Normal speech',
                'gender': 'male',
                'speakers': 1
            }
        },
        {
            'path': 'woman_voice.mp3',
            'expected': {
                'artist': 'A woman voice',
                'song': 'Normal speech',
                'gender': 'female',
                'speakers': 1
            }
        }
    ]
    
    results_summary = []
    
    for i, test in enumerate(test_files, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test['expected'].get('artist', 'Unknown Artist')}")
        print(f"{'='*70}")
        
        file_path = Path('data/audio_samples') / test['path']
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            print("   Skipping...")
            continue
        
        try:
            # Analyze
            results = analyzer.analyze_audio(str(file_path), detailed=True)
            
            # Check for errors
            if 'error' in results:
                print(f"\n⚠️  Analysis Error: {results['error']}")
                if 'reason' in results:
                    print(f"   Reason: {results['reason']}")
                
                results_summary.append({
                    'file': test['path'],
                    'artist': test['expected'].get('artist'),
                    'error': results['error'],
                    'gender_correct': False,
                    'speakers_correct': False
                })
                continue
            
            # Show summary
            print("\n" + analyzer.generate_summary(results))
            
            # Check accuracy
            print(f"\n📊 ACCURACY CHECK:")
            print("-" * 70)
            
            expected_gender = test['expected'].get('gender')
            actual_gender = results.get('gender', {}).get('classification')
            
            # Handle both/duet cases
            if expected_gender == 'both':
                print(f"   Expected: Male + Female (duet)")
                print(f"   Detected: {actual_gender or 'unknown'} "
                      f"({results.get('speaker_count', {}).get('estimated_count', 1)} speaker(s))")
                
                # Consider it correct if multiple speakers detected
                gender_correct = results.get('speaker_count', {}).get('estimated_count', 1) >= 2
                
                if gender_correct:
                    print("   ✅ CORRECT - Multiple speakers detected!")
                else:
                    print("   ⚠️  PARTIAL - Only detected 1 speaker (duets are hard!)")
            else:
                print(f"   Expected gender: {expected_gender}")
                print(f"   Detected gender: {actual_gender or 'unknown'}")
                
                gender_correct = actual_gender == expected_gender
                
                if gender_correct:
                    print("   ✅ CORRECT!")
                else:
                    print("   ❌ INCORRECT")
            
            expected_speakers = test['expected'].get('speakers', 1)
            actual_speakers = results.get('speaker_count', {}).get('estimated_count', 1)
            
            print(f"\n   Expected speakers: {expected_speakers}")
            print(f"   Detected speakers: {actual_speakers}")
            
            speakers_correct = actual_speakers == expected_speakers
            
            if speakers_correct:
                print("   ✅ CORRECT!")
            else:
                print(f"   ⚠️  DIFFERENCE ({actual_speakers} vs {expected_speakers})")
            
            # Store results
            results_summary.append({
                'file': test['path'],
                'artist': test['expected'].get('artist'),
                'expected_gender': expected_gender,
                'detected_gender': actual_gender or 'unknown',
                'gender_correct': gender_correct,
                'expected_speakers': expected_speakers,
                'detected_speakers': actual_speakers,
                'speakers_correct': speakers_correct,
                'confidence': results.get('gender', {}).get('confidence', 0),
                'pitch_hz': results.get('gender', {}).get('mean_f0', 0),
                'music_score': results.get('music_score', 0),
                'method': results.get('analysis_method', 'unknown')
            })
            
        except Exception as e:
            print(f"\n❌ Error analyzing file: {e}")
            import traceback
            traceback.print_exc()
            
            results_summary.append({
                'file': test['path'],
                'artist': test['expected'].get('artist'),
                'error': str(e),
                'gender_correct': False,
                'speakers_correct': False
            })
    
    # Overall summary
    print(f"\n{'='*70}")
    print("  OVERALL RESULTS")
    print(f"{'='*70}\n")
    
    if results_summary:
        # Filter out errors
        valid_results = [r for r in results_summary if 'error' not in r]
        
        if valid_results:
            total = len(valid_results)
            gender_correct = sum(1 for r in valid_results if r['gender_correct'])
            speakers_correct = sum(1 for r in valid_results if r['speakers_correct'])
            
            print(f"📊 Tested: {total} files (successful)")
            print(f"✅ Gender accuracy: {gender_correct}/{total} ({gender_correct/total*100:.0f}%)")
            print(f"✅ Speaker count accuracy: {speakers_correct}/{total} ({speakers_correct/total*100:.0f}%)")
            
            print(f"\n📋 DETAILED BREAKDOWN:")
            print("-" * 70)
            print(f"{'Artist':<40} | {'Gender':<12} | {'Conf':<6} | {'Pitch':<8} | {'Spkr':<4} | {'Status'}")
            print("-" * 70)
            
            for result in valid_results:
                status = "✅" if result['gender_correct'] else "❌"
                gender = result['detected_gender']
                conf = f"{result['confidence']:.0%}"
                pitch = f"{result['pitch_hz']:.0f}Hz"
                speakers = result['detected_speakers']
                artist = result['artist'][:38]
                
                print(f"{status} {artist:<38} | {gender:<12} | {conf:<6} | {pitch:<8} | {speakers:<4}")
            
            print(f"\n💡 ANALYSIS INSIGHTS:")
            print("-" * 70)
            
            # Check for low confidence
            low_conf = [r for r in valid_results if r['confidence'] < 0.5]
            if low_conf:
                print(f"⚠️  {len(low_conf)} file(s) had low confidence (<50%)")
                print("   This is normal for music with heavy production")
            
            # Check for high music score
            high_music = [r for r in valid_results if r['music_score'] > 0.8]
            if high_music:
                print(f"🎵 {len(high_music)} file(s) had heavy music (>80%)")
                print("   Voice analysis is harder with background music")
            
            # Check method used
            methods = set(r.get('method', 'unknown') for r in valid_results)
            print(f"\n🔧 Analysis method(s) used: {', '.join(methods)}")
        
        # Show errors
        error_results = [r for r in results_summary if 'error' in r]
        if error_results:
            print(f"\n❌ FAILED FILES: {len(error_results)}")
            print("-" * 70)
            for result in error_results:
                print(f"   {result['file']}: {result['error']}")
    
    print("\n" + "="*70)
    print("  TESTING COMPLETE")
    print("="*70 + "\n")
    
    print("💡 TIPS:")
    print("   - Gender detection works best with clear speech")
    print("   - Music makes detection harder but not impossible")
    print("   - pYIN pitch detection is robust for most cases")
    print("   - Speaker counting requires cleaner audio")


if __name__ == "__main__":
    test_analyzer()