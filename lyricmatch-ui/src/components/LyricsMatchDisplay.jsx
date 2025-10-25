// src/components/LyricsMatchDisplay.jsx
import React, { useState, useEffect } from 'react';
import { Sparkles, Info, Check } from 'lucide-react';

export const LyricsMatchDisplay = ({ queryText, songLyrics, matchPercentage }) => {
  const [highlightedLyrics, setHighlightedLyrics] = useState([]);
  const [matchingSegments, setMatchingSegments] = useState([]);

  useEffect(() => {
    if (queryText && songLyrics) {
      findAndHighlightMatches();
    }
  }, [queryText, songLyrics]);

  const findAndHighlightMatches = () => {
    const queryWords = queryText.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    const lyricWords = songLyrics.toLowerCase().split(/\s+/);
    const originalWords = songLyrics.split(/\s+/);
    
    // Create a map of which words match
    const matchMap = lyricWords.map((word, idx) => {
      const cleanWord = word.replace(/[^\w]/g, '');
      return queryWords.some(qw => {
        const cleanQw = qw.replace(/[^\w]/g, '');
        return cleanWord === cleanQw || 
               cleanWord.includes(cleanQw) || 
               cleanQw.includes(cleanWord);
      });
    });

    // Find consecutive matching segments
    const segments = [];
    let currentSegment = null;
    
    for (let i = 0; i < matchMap.length; i++) {
      if (matchMap[i]) {
        if (!currentSegment) {
          currentSegment = { start: i, end: i, words: [originalWords[i]] };
        } else {
          currentSegment.end = i;
          currentSegment.words.push(originalWords[i]);
        }
      } else {
        if (currentSegment && currentSegment.words.length >= 2) {
          segments.push({
            ...currentSegment,
            text: currentSegment.words.join(' ')
          });
        }
        currentSegment = null;
      }
    }
    
    // Add last segment if exists
    if (currentSegment && currentSegment.words.length >= 2) {
      segments.push({
        ...currentSegment,
        text: currentSegment.words.join(' ')
      });
    }

    // Create highlighted lyrics display
    const highlighted = [];
    let lastIdx = 0;
    
    segments.forEach(segment => {
      // Add non-matching text before segment
      if (segment.start > lastIdx) {
        highlighted.push({
          text: originalWords.slice(lastIdx, segment.start).join(' '),
          isMatch: false
        });
      }
      
      // Add matching segment
      highlighted.push({
        text: segment.text,
        isMatch: true
      });
      
      lastIdx = segment.end + 1;
    });
    
    // Add remaining text
    if (lastIdx < originalWords.length) {
      highlighted.push({
        text: originalWords.slice(lastIdx).join(' '),
        isMatch: false
      });
    }

    setHighlightedLyrics(highlighted);
    setMatchingSegments(segments.slice(0, 5)); // Top 5 segments
  };

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Lyrics Analysis
        </h3>
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold text-green-500">
            {matchPercentage.toFixed(1)}%
          </div>
          <span className="text-sm text-[var(--text-secondary)]">match</span>
        </div>
      </div>
      
      {/* Match Progress Bar */}
      <div className="mb-6">
        <div className="h-3 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-green-500 via-blue-500 to-purple-500 rounded-full transition-all duration-1000"
            style={{ width: `${matchPercentage}%` }}
          />
        </div>
      </div>

      {/* Top Matching Segments */}
      {matchingSegments.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase">
            Top Matching Phrases
          </h4>
          <div className="space-y-2">
            {matchingSegments.map((segment, idx) => (
              <div 
                key={idx}
                className="group bg-gradient-to-r from-green-500/10 to-blue-500/10 hover:from-green-500/20 hover:to-blue-500/20 border border-green-500/30 rounded-lg p-3 transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center text-white font-bold text-xs">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-[var(--text-primary)] font-medium leading-relaxed">
                      "{segment.text}"
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-1">
                      {segment.words.length} words matched
                    </p>
                  </div>
                  <Check className="w-5 h-5 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Lyrics with Highlighting */}
      <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 max-h-96 overflow-y-auto">
        <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase sticky top-0 bg-[var(--bg-tertiary)] pb-2">
          Song Lyrics (Matches Highlighted)
        </h4>
        <div className="text-[var(--text-primary)] leading-relaxed space-y-2">
          {highlightedLyrics.map((segment, idx) => (
            <span
              key={idx}
              className={segment.isMatch ? 
                'bg-gradient-to-r from-yellow-500/30 to-green-500/30 px-1 py-0.5 rounded font-semibold text-[var(--text-primary)] shadow-sm' : 
                'text-[var(--text-secondary)]'
              }
            >
              {segment.text}{' '}
            </span>
          ))}
        </div>
      </div>

      {matchingSegments.length === 0 && (
        <div className="text-center py-8 text-[var(--text-secondary)]">
          <Info className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No exact phrase matches found</p>
          <p className="text-sm mt-1">Match based on semantic similarity</p>
        </div>
      )}
    </div>
  );
};