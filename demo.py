"""
Quick demo of LyricMatch functionality
Shows all components working together
"""
from pathlib import Path
from config import Config
from src.database import LyricsDatabase
from src.text_processor import TextProcessor
from src.matcher import LyricsMatcher


def demo_database():
    """Demonstrate database functionality"""
    print("\n" + "="*60)
    print("📊 DATABASE DEMO")
    print("="*60 + "\n")
    
    try:
        with LyricsDatabase() as db:
            # Get statistics
            stats = db.get_database_stats()
            
            print(f"📚 Database Statistics:")
            print(f"   Total Songs: {stats['total_songs']:,}")
            print(f"   Total Artists: {stats['total_artists']:,}")
            print(f"   Average Words: {stats['avg_word_count']:.0f} per song")
            
            if stats['top_artists']:
                print(f"\n🌟 Top 5 Artists:")
                for i, (artist, count) in enumerate(stats['top_artists'][:5], 1):
                    print(f"   {i}. {artist}: {count} songs")
            
            # Sample search
            if stats['total_songs'] > 0:
                print(f"\n🔍 Sample Search (first artist):")
                first_artist = stats['top_artists'][0][0] if stats['top_artists'] else None
                
                if first_artist:
                    songs = db.search_by_artist(first_artist)[:3]
                    for song in songs:
                        print(f"   • {song['title']} ({song.get('year', 'N/A')})")
            
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("💡 Run: python setup_database.py")
        return False


def demo_text_processing():
    """Demonstrate text processing"""
    print("\n" + "="*60)
    print("📝 TEXT PROCESSING DEMO")
    print("="*60 + "\n")
    
    processor = TextProcessor()
    
    # Sample text (generic, not actual lyrics)
    sample = "I'm feeling GREAT today!!! 🎵 Let's dance & sing! Visit https://example.com"
    
    print(f"Original text:")
    print(f"   \"{sample}\"")
    
    cleaned = processor.clean_text(sample)
    print(f"\nCleaned text:")
    print(f"   \"{cleaned}\"")
    
    stats = processor.get_text_stats(sample)
    print(f"\nText statistics:")
    print(f"   Words: {stats['word_count']}")
    print(f"   Unique words: {stats['unique_words']}")
    print(f"   Avg word length: {stats['avg_word_length']:.1f}")
    
    return True


def demo_matching():
    """Demonstrate lyrics matching"""
    print("\n" + "="*60)
    print("🔍 LYRICS MATCHING DEMO")
    print("="*60 + "\n")
    
    try:
        with LyricsMatcher() as matcher:
            # Example query (generic phrase)
            query = "feeling good today sunshine bright"
            
            print(f"Search query: \"{query}\"")
            print(f"\nSearching {len(matcher.songs_df)} songs...\n")
            
            results = matcher.match(query, top_k=3)
            
            if results:
                print(f"✅ Found {len(results)} match(es):")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['artist']} - {result['title']}")
                    print(f"   Score: {result['final_score']:.2%}")
                    print(f"   Type: {result['match_type']}")
            else:
                print("❌ No matches found (try a different query or lower threshold)")
            
            return True
            
    except Exception as e:
        print(f"❌ Matching error: {e}")
        print("💡 Make sure database is set up: python setup_database.py")
        return False


def demo_audio_samples():
    """Check for audio samples"""
    print("\n" + "="*60)
    print("🎵 AUDIO SAMPLES CHECK")
    print("="*60 + "\n")
    
    from utils.audio_utils import AudioManager
    manager = AudioManager()
    audio_files = manager.get_audio_files()
    
    if audio_files:
        print(f"✅ Found {len(audio_files)} audio file(s):")
        for audio_file in audio_files[:5]:
            print(f"   • {audio_file.name}")
        if len(audio_files) > 5:
            print(f"   ... and {len(audio_files) - 5} more")
        
        print(f"\n💡 Test with: python main.py {audio_files[0]}")
        return True
    else:
        print(f"⚠️  No audio files found in: {Config.AUDIO_SAMPLES_DIR}")
        print(f"\n📝 To test the full pipeline:")
        print(f"   1. Add audio files to: {Config.AUDIO_SAMPLES_DIR}")
        print(f"   2. Or run: python -m utils.audio_utils download_sample_audio")
        print(f"   3. Run: python main.py <audio_file>")
        return False


def main():
    """Run complete demo"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*18 + "LYRICMATCH DEMO" + " "*25 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run demos
    results.append(("Database", demo_database()))
    results.append(("Text Processing", demo_text_processing()))
    results.append(("Lyrics Matching", demo_matching()))
    results.append(("Audio Samples", demo_audio_samples()))
    
    # Summary
    print("\n" + "="*60)
    print("📋 DEMO SUMMARY")
    print("="*60 + "\n")
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name:20s} - {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} demos successful")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\n🚀 Ready to use LyricMatch!")
        print("\n📝 Next steps:")
        print("   • Add audio files: data/audio_samples/")
        print("   • Test transcription: python test_transcription.py")
        print("   • Identify songs: python main.py <audio_file>")
    else:
        print("⚠️  Some demos failed. Check the output above.")
        
        if not results[0][1]:  # Database failed
            print("\n💡 Quick fix: python setup_database.py")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())