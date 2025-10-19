"""
Configuration settings for LyricMatch
Enhanced with neural embeddings support
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Main configuration class"""
    
    # Directory paths
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    AUDIO_SAMPLES_DIR = DATA_DIR / "audio_samples"
    MODELS_DIR = BASE_DIR / "models"
    
    # Database
    DB_PATH = PROCESSED_DATA_DIR / "lyrics.db"
    LYRICS_CSV_PATH = PROCESSED_DATA_DIR / "lyrics.csv"
    
    # Whisper Model Settings
    WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
    WHISPER_LANGUAGE = None  # None = auto-detect language
    
    # Audio Processing Settings
    SAMPLE_RATE = 16000
    AUDIO_DURATION_LIMIT = 60  # Maximum audio duration in seconds
    SUPPORTED_FORMATS = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    
    # Text Processing Settings
    MIN_LYRIC_LENGTH = 10  # Minimum characters for valid lyrics
    MAX_LYRIC_LENGTH = 5000  # Maximum characters
    
    # Matching Settings - General
    SIMILARITY_THRESHOLD = 0.25  # Minimum similarity score (0-1)
    TOP_K_RESULTS = 5  # Number of top matches to return
    USE_FUZZY_MATCHING = True
    
    # Matching Engine Selection
    MATCHING_ENGINE = "neural"  # Options: "tfidf", "neural", "hybrid"
    
    # Neural Embeddings Settings (Sentence-BERT)
    SBERT_MODEL = "all-MiniLM-L6-v2"  # Default SBERT model
    """
    Available SBERT models:
    - 'all-MiniLM-L6-v2': Fast, 384 dimensions, good quality (RECOMMENDED)
    - 'all-mpnet-base-v2': Best quality, 768 dimensions, slower
    - 'paraphrase-MiniLM-L6-v2': Good for paraphrases, 384 dimensions
    - 'all-MiniLM-L12-v2': Better quality, 384 dimensions, medium speed
    - 'multi-qa-MiniLM-L6-cos-v1': Optimized for Q&A, 384 dimensions
    """
    
    USE_EMBEDDINGS_CACHE = True  # Cache embeddings to disk
    HYBRID_NEURAL_WEIGHT = 0.7  # Weight for neural vs fuzzy (0-1)
    
    # TF-IDF Settings (Legacy/Comparison)
    VECTORIZER = "tfidf"  # Options: tfidf, embeddings
    NGRAM_RANGE = (1, 3)  # For TF-IDF
    MAX_FEATURES = 5000  # For TF-IDF
    
    # API Settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    DEBUG = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi',
        # ... (90+ languages supported)
    }
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.AUDIO_SAMPLES_DIR,
            cls.MODELS_DIR,
            cls.MODELS_DIR / "embeddings_cache"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        print("✅ Directory structure created successfully")
    
    @classmethod
    def get_info(cls):
        """Print configuration information"""
        lang_status = f"Auto-detect ({len(cls.SUPPORTED_LANGUAGES)}+ languages)" if cls.WHISPER_LANGUAGE is None else cls.SUPPORTED_LANGUAGES.get(cls.WHISPER_LANGUAGE, cls.WHISPER_LANGUAGE)
        
        info = f"""
        ╔══════════════════════════════════════════╗
        ║         LyricMatch Configuration          ║
        ╚══════════════════════════════════════════╝
        
        📁 Directories:
           - Data: {cls.DATA_DIR}
           - Database: {cls.DB_PATH}
           - Models: {cls.MODELS_DIR}
        
        🎤 Whisper Settings:
           - Model: {cls.WHISPER_MODEL}
           - Language: {lang_status}
        
        🔍 Matching Settings:
           - Engine: {cls.MATCHING_ENGINE.upper()}
           - Similarity Threshold: {cls.SIMILARITY_THRESHOLD}
           - Top Results: {cls.TOP_K_RESULTS}
        
        🧠 Neural Embeddings:
           - Model: {cls.SBERT_MODEL}
           - Cache Enabled: {cls.USE_EMBEDDINGS_CACHE}
           - Hybrid Weight: {cls.HYBRID_NEURAL_WEIGHT}
        
        📊 TF-IDF Settings:
           - Vectorizer: {cls.VECTORIZER}
           - N-gram Range: {cls.NGRAM_RANGE}
           - Max Features: {cls.MAX_FEATURES}
        
        🌐 API Settings:
           - Host: {cls.API_HOST}
           - Port: {cls.API_PORT}
        """
        return info
    
    @classmethod
    def set_matching_engine(cls, engine):
        """
        Set the matching engine
        
        Args:
            engine: 'tfidf', 'neural', or 'hybrid'
        """
        valid_engines = ['tfidf', 'neural', 'hybrid']
        if engine.lower() not in valid_engines:
            print(f"⚠️  Invalid engine. Choose from: {', '.join(valid_engines)}")
            return
        
        cls.MATCHING_ENGINE = engine.lower()
        print(f"✅ Matching engine set to: {cls.MATCHING_ENGINE.upper()}")
    
    @classmethod
    def set_sbert_model(cls, model_name):
        """
        Set the Sentence-BERT model
        
        Args:
            model_name: SBERT model name
        """
        cls.SBERT_MODEL = model_name
        print(f"✅ SBERT model set to: {model_name}")
        print("⚠️  Note: Embeddings cache will need to be rebuilt")
    
    @classmethod
    def list_sbert_models(cls):
        """Print list of recommended SBERT models"""
        print("\n🧠 Recommended Sentence-BERT Models:")
        print("="*60)
        
        models = [
            ("all-MiniLM-L6-v2", "384 dims", "Fast", "Good quality", "⭐ RECOMMENDED"),
            ("all-mpnet-base-v2", "768 dims", "Slower", "Best quality", "🏆 HIGHEST QUALITY"),
            ("all-MiniLM-L12-v2", "384 dims", "Medium", "Better quality", ""),
            ("paraphrase-MiniLM-L6-v2", "384 dims", "Fast", "Good for paraphrases", ""),
            ("multi-qa-MiniLM-L6-cos-v1", "384 dims", "Fast", "Optimized for Q&A", ""),
        ]
        
        for name, dims, speed, desc, badge in models:
            badge_str = f" {badge}" if badge else ""
            print(f"\n📦 {name}{badge_str}")
            print(f"   Dimensions: {dims} | Speed: {speed}")
            print(f"   {desc}")
        
        print("\n💡 More models at: https://www.sbert.net/docs/pretrained_models.html")


# Create directories on import
Config.create_directories()

if __name__ == "__main__":
    print(Config.get_info())
    print("\n")
    Config.list_sbert_models()