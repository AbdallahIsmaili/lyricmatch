"""
Voice-Enhanced Matcher
Combines song matching with voice analysis context
"""
from src.neural_matcher import NeuralLyricsMatcher
from src.voice_analyzer import VoiceAnalyzer


class VoiceEnhancedMatcher(NeuralLyricsMatcher):
    """Matcher that uses voice context to improve results"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voice_analyzer = VoiceAnalyzer()
    
    def match_with_voice_context(self, audio_path, transcribed_text, top_k=5):
        """
        Match songs considering voice characteristics
        
        This can help filter results (e.g., if voice is clearly female,
        prioritize songs by female artists)
        """
        # Get voice analysis
        voice_analysis = self.voice_analyzer.analyze_audio(audio_path)
        
        # Get standard matches
        results = self.match(transcribed_text, top_k=top_k * 2)
        
        # Enhance results with voice context
        for result in results:
            result['voice_analysis'] = voice_analysis
            
            # Optional: Adjust scores based on voice-artist match
            # This would require artist gender info in database
            # result['voice_adjusted_score'] = self._adjust_for_voice(result, voice_analysis)
        
        return results[:top_k]