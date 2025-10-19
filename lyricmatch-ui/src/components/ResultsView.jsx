import React from 'react';
import { Music, Trophy, Medal, Award, RefreshCw } from 'lucide-react';

const ResultsView = ({ results, onReset }) => {
  console.log('🎨 ResultsView rendered with:', results);

  if (!results || !results.topMatch) {
    return (
      <div className="text-center text-white">
        <p>No results to display</p>
        <button 
          onClick={onReset}
          className="mt-4 px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg"
        >
          Try Again
        </button>
      </div>
    );
  }

  const { topMatch, alternatives, transcription, language, audioInfo } = results;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Success Message */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full mb-4">
          <Trophy className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-4xl font-bold text-white mb-2">
          Match Found!
        </h2>
        <p className="text-white/60">
          We identified your song with {Math.round(topMatch.final_score * 100)}% confidence
        </p>
      </div>

      {/* Top Match - Large Card */}
      <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
        <div className="flex items-start gap-6">
          <div className="flex-shrink-0">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
              <Music className="w-12 h-12 text-white" />
            </div>
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Trophy className="w-6 h-6 text-yellow-400" />
              <span className="text-sm font-semibold text-yellow-400 uppercase tracking-wider">
                Best Match
              </span>
            </div>
            
            <h3 className="text-3xl font-bold text-white mb-2">
              {topMatch.title}
            </h3>
            
            <p className="text-xl text-purple-200 mb-4">
              by {topMatch.artist}
            </p>

            <div className="grid grid-cols-2 gap-4 mb-4">
              {topMatch.album && (
                <div>
                  <p className="text-sm text-white/50">Album</p>
                  <p className="text-white font-medium">{topMatch.album}</p>
                </div>
              )}
              {topMatch.year && (
                <div>
                  <p className="text-sm text-white/50">Year</p>
                  <p className="text-white font-medium">{topMatch.year}</p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white/70">Confidence</span>
                  <span className="text-white font-semibold">
                    {Math.round(topMatch.final_score * 100)}%
                  </span>
                </div>
                <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-1000"
                    style={{ width: `${topMatch.final_score * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alternative Matches */}
      {alternatives && alternatives.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Medal className="w-5 h-5 text-gray-400" />
            Alternative Matches
          </h3>
          <div className="space-y-3">
            {alternatives.map((match, index) => (
              <div 
                key={index}
                className="bg-white/5 backdrop-blur-xl rounded-xl p-4 border border-white/10 hover:bg-white/10 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-1">
                      {match.title}
                    </h4>
                    <p className="text-purple-200">
                      {match.artist}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">
                      {Math.round(match.final_score * 100)}%
                    </div>
                    <div className="text-sm text-white/50">
                      {match.year || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transcription Info */}
      {transcription && (
        <div className="bg-white/5 backdrop-blur-xl rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
            <Music className="w-5 h-5" />
            Transcription Details
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-white/60">Language:</span>
              <span className="text-white font-medium">{language || 'Unknown'}</span>
            </div>
            {audioInfo && (
              <>
                <div className="flex justify-between">
                  <span className="text-white/60">Duration:</span>
                  <span className="text-white font-medium">
                    {audioInfo.duration?.toFixed(1)}s
                  </span>
                </div>
              </>
            )}
            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-white/60 text-xs mb-2">Transcribed Text:</p>
              <p className="text-white/80 text-sm italic line-clamp-3">
                "{transcription.substring(0, 200)}..."
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Try Again Button */}
      <div className="text-center pt-6">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl shadow-lg transition-all transform hover:scale-105"
        >
          <RefreshCw className="w-5 h-5" />
          Analyze Another Song
        </button>
      </div>
    </div>
  );
};

export default ResultsView;