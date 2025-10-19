"""
Text processing module for cleaning and normalizing lyrics
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class TextProcessor:
    """Process and normalize text for matching"""
    
    def __init__(self, remove_stopwords=False, lowercase=True):
        """
        Initialize text processor
        
        Args:
            remove_stopwords: Whether to remove common words
            lowercase: Convert text to lowercase
        """
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
        
        if remove_stopwords:
            self.stop_words = set(stopwords.words('english'))
        else:
            self.stop_words = set()
    
    def clean_text(self, text):
        """
        Clean and normalize text
        
        Args:
            text: Input text string
        
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase if specified
        if self.lowercase:
            text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep apostrophes and hyphens
        text = re.sub(r'[^\w\s\'\-]', ' ', text)
        
        # Remove numbers (optional - songs sometimes have numbers in lyrics)
        # text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def remove_punctuation(self, text):
        """Remove all punctuation from text"""
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
    
    def tokenize(self, text):
        """
        Tokenize text into words
        
        Args:
            text: Input text
        
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback to simple split if NLTK tokenizer fails
            tokens = text.split()
        
        return tokens
    
    def process_text(self, text, remove_punctuation=False):
        """
        Complete text processing pipeline
        
        Args:
            text: Input text
            remove_punctuation: Whether to remove punctuation
        
        Returns:
            Processed text
        """
        # Clean text
        text = self.clean_text(text)
        
        # Remove punctuation if requested
        if remove_punctuation:
            text = self.remove_punctuation(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords if specified
        if self.remove_stopwords:
            tokens = [word for word in tokens if word not in self.stop_words]
        
        # Rejoin tokens
        processed_text = ' '.join(tokens)
        
        return processed_text
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract most important words from text
        
        Args:
            text: Input text
            top_n: Number of keywords to return
        
        Returns:
            List of keywords
        """
        # Process text
        text = self.clean_text(text)
        tokens = self.tokenize(text)
        
        # Remove stopwords and short words
        keywords = [
            word for word in tokens 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(keywords)
        
        # Return top N most common
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def calculate_similarity_simple(self, text1, text2):
        """
        Calculate simple word overlap similarity
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        # Process both texts
        words1 = set(self.tokenize(self.clean_text(text1)))
        words2 = set(self.tokenize(self.clean_text(text2)))
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0.0
        
        return similarity
    
    def get_text_stats(self, text):
        """
        Get statistics about text
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of statistics
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        
        stats = {
            'original_length': len(text),
            'cleaned_length': len(cleaned),
            'word_count': len(tokens),
            'unique_words': len(set(tokens)),
            'avg_word_length': sum(len(word) for word in tokens) / len(tokens) if tokens else 0,
            'char_count': len(cleaned.replace(' ', ''))
        }
        
        return stats


def test_text_processor():
    """Test the text processor"""
    print("\n" + "="*60)
    print("Testing Text Processor")
    print("="*60 + "\n")
    
    processor = TextProcessor(remove_stopwords=False, lowercase=True)
    
    # Test text (example, not from any actual song)
    test_text = """
    I'm feeling good today! 🎵
    The sun is shining bright...
    Let's dance and sing along - yeah yeah!
    Visit https://example.com for more
    """
    
    print("Original text:")
    print(test_text)
    
    print("\n" + "-"*60)
    print("Cleaned text:")
    cleaned = processor.clean_text(test_text)
    print(cleaned)
    
    print("\n" + "-"*60)
    print("Processed text:")
    processed = processor.process_text(test_text)
    print(processed)
    
    print("\n" + "-"*60)
    print("Keywords:")
    keywords = processor.extract_keywords(test_text, top_n=5)
    print(keywords)
    
    print("\n" + "-"*60)
    print("Text statistics:")
    stats = processor.get_text_stats(test_text)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test similarity
    text1 = "i love to dance and sing"
    text2 = "dancing and singing is fun"
    similarity = processor.calculate_similarity_simple(text1, text2)
    print(f"\n" + "-"*60)
    print(f"Similarity between texts: {similarity:.2%}")


if __name__ == "__main__":
    test_text_processor()