"""
Database module for managing song lyrics
Processes CSV files and creates searchable database
"""
import pandas as pd
import sqlite3
from pathlib import Path
import re
from tqdm import tqdm

from config import Config


class LyricsDatabase:
    """Manage song lyrics database"""
    
    def __init__(self, db_path=None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or Config.DB_PATH
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Create database connection"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✅ Connected to database: {self.db_path}")
    
    def create_tables(self):
        """Create database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                title TEXT NOT NULL,
                album TEXT,
                year INTEGER,
                date TEXT,
                lyrics TEXT NOT NULL,
                lyrics_cleaned TEXT,
                word_count INTEGER,
                char_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(artist, title)
            )
        ''')
        
        # Create index for faster searching
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_artist ON songs(artist)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_title ON songs(title)
        ''')
        
        self.conn.commit()
        print("✅ Database tables created")
    
    def load_csv_files(self, csv_dir=None):
        """
        Load all CSV files from directory
        
        Args:
            csv_dir: Directory containing CSV files
        
        Returns:
            Number of songs loaded
        """
        if csv_dir is None:
            csv_dir = Config.RAW_DATA_DIR / "csv"
        
        csv_dir = Path(csv_dir)
        
        if not csv_dir.exists():
            raise FileNotFoundError(f"CSV directory not found: {csv_dir}")
        
        csv_files = list(csv_dir.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in: {csv_dir}")
        
        print(f"\n📂 Found {len(csv_files)} CSV files")
        print("="*60)
        
        total_songs = 0
        
        for csv_file in tqdm(csv_files, desc="Loading CSV files"):
            try:
                songs_added = self._load_single_csv(csv_file)
                total_songs += songs_added
            except Exception as e:
                print(f"\n⚠️  Error loading {csv_file.name}: {e}")
                continue
        
        print(f"\n✅ Total songs loaded: {total_songs}")
        return total_songs
    
    def _load_single_csv(self, csv_path):
        """Load a single CSV file"""
        try:
            # Read CSV - handle the duplicate columns issue
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Drop the first unnamed column if it exists
            if df.columns[0] == 'Unnamed: 0' or df.columns[0] == '':
                df = df.iloc[:, 1:]
            
            # Handle duplicate columns by keeping only the first set
            # Your CSV has duplicate columns, so we'll take the first 6 columns
            expected_cols = ['Artist', 'Title', 'Album', 'Year', 'Date', 'Lyric']
            
            if len(df.columns) >= 6:
                df = df.iloc[:, :6]
                df.columns = expected_cols
            
            songs_added = 0
            
            for _, row in df.iterrows():
                try:
                    # Skip if lyrics are empty or too short
                    lyrics = str(row['Lyric'])
                    if pd.isna(lyrics) or len(lyrics) < Config.MIN_LYRIC_LENGTH:
                        continue
                    
                    # Clean and prepare data
                    artist = str(row['Artist']).strip()
                    title = str(row['Title']).strip()
                    album = str(row['Album']) if pd.notna(row['Album']) else None
                    year = int(row['Year']) if pd.notna(row['Year']) else None
                    date = str(row['Date']) if pd.notna(row['Date']) else None
                    
                    # Insert into database
                    self._insert_song(artist, title, album, year, date, lyrics)
                    songs_added += 1
                    
                except Exception as e:
                    continue
            
            return songs_added
            
        except Exception as e:
            raise Exception(f"Error reading CSV: {e}")
    
    def _insert_song(self, artist, title, album, year, date, lyrics):
        """Insert a song into the database"""
        # Clean lyrics for searching (remove extra spaces, normalize)
        lyrics_cleaned = self._clean_lyrics(lyrics)
        word_count = len(lyrics_cleaned.split())
        char_count = len(lyrics_cleaned)
        
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO songs 
                (artist, title, album, year, date, lyrics, lyrics_cleaned, word_count, char_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (artist, title, album, year, date, lyrics, lyrics_cleaned, word_count, char_count))
            
            self.conn.commit()
            
        except sqlite3.IntegrityError:
            pass  # Song already exists
    
    def _clean_lyrics(self, lyrics):
        """Clean lyrics text for better matching"""
        # Convert to lowercase
        lyrics = lyrics.lower()
        
        # Remove special characters but keep basic punctuation
        lyrics = re.sub(r'[^\w\s\'\-]', ' ', lyrics)
        
        # Remove extra whitespace
        lyrics = ' '.join(lyrics.split())
        
        return lyrics
    
    def get_all_songs(self):
        """Get all songs from database"""
        self.cursor.execute('SELECT * FROM songs')
        columns = [description[0] for description in self.cursor.description]
        songs = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return songs
    
    def get_song_count(self):
        """Get total number of songs in database"""
        self.cursor.execute('SELECT COUNT(*) FROM songs')
        return self.cursor.fetchone()[0]
    
    def search_by_artist(self, artist):
        """Search songs by artist name"""
        self.cursor.execute('''
            SELECT * FROM songs 
            WHERE LOWER(artist) LIKE LOWER(?)
        ''', (f'%{artist}%',))
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def search_by_title(self, title):
        """Search songs by title"""
        self.cursor.execute('''
            SELECT * FROM songs 
            WHERE LOWER(title) LIKE LOWER(?)
        ''', (f'%{title}%',))
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_database_stats(self):
        """Get database statistics"""
        stats = {}
        
        # Total songs
        stats['total_songs'] = self.get_song_count()
        
        # Unique artists
        self.cursor.execute('SELECT COUNT(DISTINCT artist) FROM songs')
        stats['total_artists'] = self.cursor.fetchone()[0]
        
        # Average lyrics length
        self.cursor.execute('SELECT AVG(word_count) FROM songs')
        stats['avg_word_count'] = round(self.cursor.fetchone()[0] or 0, 2)
        
        # Songs per artist (top 10)
        self.cursor.execute('''
            SELECT artist, COUNT(*) as count 
            FROM songs 
            GROUP BY artist 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_artists'] = self.cursor.fetchall()
        
        return stats
    
    def export_to_csv(self, output_path=None):
        """Export database to CSV"""
        if output_path is None:
            output_path = Config.PROCESSED_DATA_DIR / "all_songs.csv"
        
        df = pd.DataFrame(self.get_all_songs())
        df.to_csv(output_path, index=False)
        print(f"✅ Exported to: {output_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def setup_database():
    """Setup database from CSV files"""
    print("\n" + "="*60)
    print("📊 Setting Up Lyrics Database")
    print("="*60 + "\n")
    
    with LyricsDatabase() as db:
        # Create tables
        db.create_tables()
        
        # Load CSV files
        csv_dir = Config.RAW_DATA_DIR / "csv"
        
        if not csv_dir.exists():
            print(f"⚠️  CSV directory not found: {csv_dir}")
            print("   Please add your CSV files there first")
            return
        
        # Load all CSV files
        total_songs = db.load_csv_files(csv_dir)
        
        # Show statistics
        print("\n" + "="*60)
        print("📈 Database Statistics")
        print("="*60)
        
        stats = db.get_database_stats()
        print(f"\n📚 Total Songs: {stats['total_songs']}")
        print(f"🎤 Total Artists: {stats['total_artists']}")
        print(f"📝 Average Words per Song: {stats['avg_word_count']}")
        
        print(f"\n🌟 Top Artists:")
        for artist, count in stats['top_artists']:
            print(f"   {artist}: {count} songs")
        
        # Export processed data
        print(f"\n💾 Exporting processed data...")
        db.export_to_csv()
        
        print("\n✅ Database setup complete!")


if __name__ == "__main__":
    setup_database()