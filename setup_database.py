"""
Setup script to initialize the lyrics database from CSV files
Run this once to process your CSV files
"""
from src.database import LyricsDatabase
from config import Config
from pathlib import Path


def main():
    """Main setup function"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*10 + "LYRICMATCH DATABASE SETUP" + " "*23 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Check if CSV directory exists
    csv_dir = Config.RAW_DATA_DIR / "csv"
    
    if not csv_dir.exists():
        print(f"❌ CSV directory not found: {csv_dir}")
        print("\n📋 Please ensure your CSV files are in:")
        print(f"   {csv_dir}")
        return 1
    
    # List CSV files
    csv_files = list(csv_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in: {csv_dir}")
        print("\n📋 Add your artist CSV files (e.g., BillieEilish.csv) to:")
        print(f"   {csv_dir}")
        return 1
    
    print(f"📂 Found {len(csv_files)} CSV file(s):")
    for csv_file in csv_files[:10]:  # Show first 10
        print(f"   • {csv_file.name}")
    if len(csv_files) > 10:
        print(f"   ... and {len(csv_files) - 10} more")
    
    # Confirm before proceeding
    print(f"\n⚠️  This will create/update the database at:")
    print(f"   {Config.DB_PATH}")
    
    response = input("\n Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Setup cancelled")
        return 0
    
    # Setup database
    print("\n" + "="*60)
    print("🔄 Processing CSV files...")
    print("="*60 + "\n")
    
    try:
        with LyricsDatabase() as db:
            # Create tables
            db.create_tables()
            
            # Load CSV files
            total_songs = db.load_csv_files(csv_dir)
            
            # Show statistics
            print("\n" + "="*60)
            print("📈 Database Statistics")
            print("="*60)
            
            stats = db.get_database_stats()
            print(f"\n📚 Total Songs: {stats['total_songs']:,}")
            print(f"🎤 Total Artists: {stats['total_artists']:,}")
            print(f"📝 Average Words per Song: {stats['avg_word_count']:.0f}")
            
            if stats['top_artists']:
                print(f"\n🌟 Top 10 Artists by Song Count:")
                for i, (artist, count) in enumerate(stats['top_artists'], 1):
                    print(f"   {i:2d}. {artist:30s} - {count:4d} songs")
            
            # Export processed data
            print(f"\n💾 Exporting processed data...")
            db.export_to_csv()
            
            print("\n" + "="*60)
            print("✅ Database setup complete!")
            print("="*60)
            
            print(f"\n📍 Database location: {Config.DB_PATH}")
            print(f"📊 CSV export: {Config.PROCESSED_DATA_DIR / 'all_songs.csv'}")
            
            print("\n🎯 Next Steps:")
            print("   1. Add audio samples to: data/audio_samples/")
            print("   2. Test transcription: python test_transcription.py")
            print("   3. Run full matching: python main.py")
            
            return 0
            
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())