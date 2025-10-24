"""
Lyrics fetching from Genius API - FIXED VERSION
"""
import requests
import os
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re

from config import Config
from src.database import LyricsDatabase

class LyricsFetcher:
    def __init__(self, genius_token=None):
        self.genius_token = genius_token or os.getenv('GENIUS_API_TOKEN')
        if not self.genius_token:
            raise ValueError("Genius API token not found. Set GENIUS_API_TOKEN in .env")
        
        self.base_url = "https://api.genius.com"
        self.headers = {'Authorization': f'Bearer {self.genius_token}'}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def search_artist_songs(self, artist_name, max_songs=50):
        """Search for artist and get their songs from Genius"""
        print(f"\n🔍 Searching for artist: {artist_name}")
        
        # Search for artist
        search_url = f"{self.base_url}/search"
        params = {'q': artist_name}
        
        response = self.session.get(search_url, params=params)
        if response.status_code != 200:
            raise Exception(f"Genius API error: {response.status_code}")
        
        data = response.json()
        
        # Find artist ID from search results
        artist_id = None
        for hit in data['response']['hits']:
            if hit['result']['primary_artist']['name'].lower() == artist_name.lower():
                artist_id = hit['result']['primary_artist']['id']
                artist_name = hit['result']['primary_artist']['name']
                break
        
        if not artist_id:
            if data['response']['hits']:
                artist_id = data['response']['hits'][0]['result']['primary_artist']['id']
                artist_name = data['response']['hits'][0]['result']['primary_artist']['name']
                print(f"⚠️  Using closest match: {artist_name}")
            else:
                raise Exception(f"Artist '{artist_name}' not found on Genius")
        
        print(f"✅ Found artist: {artist_name} (ID: {artist_id})")
        
        # Get artist's songs
        songs = []
        page = 1
        per_page = 20
        
        while len(songs) < max_songs:
            artist_url = f"{self.base_url}/artists/{artist_id}/songs"
            params = {
                'per_page': per_page,
                'page': page,
                'sort': 'popularity'
            }
            
            response = self.session.get(artist_url, params=params)
            if response.status_code != 200:
                break
            
            data = response.json()
            page_songs = data['response']['songs']
            
            if not page_songs:
                break
            
            for song in page_songs:
                if song['primary_artist']['id'] == artist_id:
                    songs.append(song)
            
            print(f"📄 Fetched page {page} ({len(songs)} songs so far)")
            page += 1
            time.sleep(0.5)
            
            if len(songs) >= max_songs:
                break
        
        songs = songs[:max_songs]
        print(f"✅ Found {len(songs)} songs for {artist_name}")
        return songs, artist_name
    
    def get_song_lyrics(self, song_url):
        """Scrape lyrics from Genius song page - IMPROVED VERSION"""
        try:
            response = requests.get(song_url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find lyrics container
            lyrics_divs = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
            
            if not lyrics_divs:
                return None
            
            lyrics = []
            for div in lyrics_divs:
                lyrics.append(div.get_text(separator='\n'))
            
            full_lyrics = '\n'.join(lyrics).strip()
            
            # IMPROVED CLEANING
            # Remove section headers like [Verse 1], [Chorus], etc.
            full_lyrics = re.sub(r'\[.*?\]', '', full_lyrics)
            
            # Remove "X Contributors" at the start
            full_lyrics = re.sub(r'^\d+\s+Contributors?.*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove "Translations" section
            full_lyrics = re.sub(r'^Translations.*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove language names (Polski, Español, etc.) that appear in a line
            full_lyrics = re.sub(r'^(Polski|Español|Česky|Italiano|Português|Deutsch|Français|Русский|日本語|한국어|中文).*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove "X Lyrics" header (e.g., "Sweet but Psycho Lyrics")
            full_lyrics = re.sub(r'^.*?\s+Lyrics$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove "Read More" and similar text
            full_lyrics = re.sub(r'Read More.*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove URLs
            full_lyrics = re.sub(r'http\S+', '', full_lyrics)
            
            # Remove metadata lines that contain "said in an interview"
            full_lyrics = re.sub(r'^.*?said in an interview.*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove description paragraphs (usually start with "The track is" or similar)
            full_lyrics = re.sub(r'^(The track|This song|The song).*?$', '', full_lyrics, flags=re.MULTILINE)
            
            # Remove lines with only special characters or numbers
            lines = full_lyrics.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Skip empty lines, lines with only punctuation, or very short lines
                if len(line) > 2 and not re.match(r'^[\d\W]+$', line):
                    cleaned_lines.append(line)
            
            full_lyrics = '\n'.join(cleaned_lines)
            
            # Remove excessive newlines (more than 2 in a row)
            full_lyrics = re.sub(r'\n{3,}', '\n\n', full_lyrics)
            
            return full_lyrics.strip()
            
        except Exception as e:
            print(f"⚠️  Error fetching lyrics: {e}")
            return None
    
    def fetch_artist_complete(self, artist_name, max_songs=50):
        """Complete pipeline: search + fetch lyrics + save"""
        print(f"\n{'='*60}")
        print(f"🎵 Fetching complete discography for: {artist_name}")
        print(f"{'='*60}\n")
        
        # Search for songs
        songs_meta, exact_artist_name = self.search_artist_songs(artist_name, max_songs)
        
        # Fetch lyrics for each song
        results = []
        for i, song_meta in enumerate(songs_meta, 1):
            print(f"\n[{i}/{len(songs_meta)}] {song_meta['title']}")
            
            lyrics = self.get_song_lyrics(song_meta['url'])
            
            if lyrics and len(lyrics) > 50:
                results.append({
                    'Artist': exact_artist_name,
                    'Title': song_meta['title'],
                    'Album': song_meta.get('album', {}).get('name', '') if song_meta.get('album') else '',
                    'Year': song_meta.get('release_date_components', {}).get('year', '') if song_meta.get('release_date_components') else '',
                    'Date': song_meta.get('release_date_for_display', ''),
                    'Lyric': lyrics
                })
                print(f"   ✅ Lyrics fetched ({len(lyrics)} chars)")
            else:
                print(f"   ⚠️  No lyrics found")
            
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully fetched {len(results)} songs with lyrics")
        print(f"{'='*60}\n")
        
        # Save to CSV
        csv_path = self._save_to_csv(results, exact_artist_name)
        
        # Add to database
        added_count = self._add_to_database(results)
        
        print(f"\n✅ Complete! Added {added_count} songs to database")
        print(f"📁 CSV saved: {csv_path}")
        
        return results
    
    def _save_to_csv(self, results, artist_name):
        """Save results to CSV in raw data folder"""
        if not results:
            return None
        
        safe_name = re.sub(r'[^\w\s-]', '', artist_name).strip().replace(' ', '')
        csv_path = Config.RAW_DATA_DIR / "csv" / f"{safe_name}.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=True)
        
        print(f"💾 Saved to: {csv_path}")
        return csv_path
    
    def _add_to_database(self, results):
        """Add songs to database and trigger index rebuild"""
        if not results:
            return 0
        
        print(f"\n📊 Adding songs to database...")
        
        with LyricsDatabase() as db:
            added = 0
            for song in results:
                try:
                    db._insert_song(
                        artist=song['Artist'],
                        title=song['Title'],
                        album=song['Album'],
                        year=int(song['Year']) if song['Year'] else None,
                        date=song['Date'],
                        lyrics=song['Lyric']
                    )
                    added += 1
                except Exception as e:
                    print(f"⚠️  Error adding {song['Title']}: {e}")
                    continue
        
        if added > 0:
            print(f"\n🔄 Rebuilding search indexes for {added} new songs...")
            self._rebuild_indexes()
        
        return added
    
    def _rebuild_indexes(self):
        """Rebuild TF-IDF and neural embedding indexes after adding songs"""
        try:
            # Rebuild TF-IDF matcher
            print("📊 Rebuilding TF-IDF index...")
            from src.matcher import LyricsMatcher
            matcher = LyricsMatcher()
            print(f"   ✅ TF-IDF index rebuilt ({len(matcher.songs_df)} songs)")
            matcher.close()
            
            # Rebuild neural embeddings
            print("🧠 Rebuilding neural embeddings...")
            from src.neural_matcher import NeuralLyricsMatcher
            neural_matcher = NeuralLyricsMatcher(use_cache=True)
            neural_matcher.rebuild_embeddings()
            print(f"   ✅ Neural embeddings rebuilt ({len(neural_matcher.songs_df)} songs)")
            neural_matcher.close()
            
            print("✅ All indexes rebuilt successfully!")
            
        except Exception as e:
            print(f"⚠️  Error rebuilding indexes: {e}")
            print("   You may need to restart the API server for changes to take effect.")