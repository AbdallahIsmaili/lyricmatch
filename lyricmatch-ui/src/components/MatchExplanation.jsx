// src/components/MatchExplanation.jsx
import React from 'react';
import { Info, Crown } from 'lucide-react';

export const MatchExplanation = ({ match, tier, engine }) => {
  const getExplanation = () => {
    const score = match.final_score * 100;
    const explanations = [];

    if (engine === 'tfidf') {
      explanations.push({
        icon: '📊',
        title: 'TF-IDF Keyword Matching',
        description: 'Analyzed word frequency and importance in the lyrics'
      });
      
      if (score > 70) {
        explanations.push({
          icon: '✅',
          title: 'Strong Keyword Overlap',
          description: `Found ${match.common_word_count || 'many'} matching keywords`
        });
      }
    } else if (engine === 'neural' || engine === 'hybrid') {
      explanations.push({
        icon: '🧠',
        title: 'Neural Semantic Analysis',
        description: 'Used AI to understand meaning and context, not just keywords'
      });
      
      if (match.neural_score && match.neural_score > 0.6) {
        explanations.push({
          icon: '🎯',
          title: 'High Semantic Similarity',
          description: 'The AI detected strong contextual meaning similarity'
        });
      }
      
      if (engine === 'hybrid' && match.fuzzy_score) {
        explanations.push({
          icon: '🔀',
          title: 'Fuzzy Matching Applied',
          description: 'Additional string matching for higher accuracy'
        });
      }
    }

    if (match.match_percentage && match.match_percentage > 50) {
      explanations.push({
        icon: '💯',
        title: `${match.match_percentage.toFixed(0)}% Word Match`,
        description: 'High percentage of words from your audio found in this song'
      });
    }

    if (score > 80) {
      explanations.push({
        icon: '⭐',
        title: 'Excellent Confidence',
        description: 'Very high likelihood this is the correct song'
      });
    } else if (score > 60) {
      explanations.push({
        icon: '👍',
        title: 'Good Confidence',
        description: 'Strong match, likely the correct song'
      });
    } else if (score > 40) {
      explanations.push({
        icon: '🤔',
        title: 'Moderate Confidence',
        description: 'Possible match, but verify with alternatives'
      });
    }

    return explanations;
  };

  const explanations = getExplanation();

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
        <Info className="w-5 h-5" />
        Why This Match?
      </h3>
      
      <div className="space-y-4">
        {explanations.map((exp, idx) => (
          <div key={idx} className="flex items-start gap-4">
            <div className="text-3xl">{exp.icon}</div>
            <div className="flex-1">
              <h4 className="font-semibold text-[var(--text-primary)] mb-1">
                {exp.title}
              </h4>
              <p className="text-[var(--text-secondary)] text-sm">
                {exp.description}
              </p>
            </div>
          </div>
        ))}
        
        <div className="mt-6 pt-4 border-t border-[var(--border)]">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[var(--text-tertiary)]">Match Type:</span>
            <span className="font-mono font-bold text-[var(--text-primary)]">
              {match.match_type?.toUpperCase()}
            </span>
          </div>
          {tier === 'premium' && (
            <div className="mt-2 flex items-center gap-2">
              <Crown className="w-4 h-4 text-yellow-500" />
              <span className="text-xs text-yellow-500 font-semibold">
                Enhanced with Premium AI models
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};