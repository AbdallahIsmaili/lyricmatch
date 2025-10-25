// src/components/ResultsView.jsx
import React, { useState, useEffect } from 'react';
import { Trophy, RefreshCw, Activity, Music, Loader2 } from 'lucide-react';
import { TierBadge } from './TierBadge';
import { StreamingButton } from './StreamingButton';
import { MatchExplanation } from './MatchExplanation';
import { LyricsMatchDisplay } from './LyricsMatchDisplay';
import { fetchSpotifyTrack, fetchYouTubeVideo } from '../utils/api';

export const ResultsView = ({ results, onReset, tier, config }) => {
  const [spotifyData, setSpotifyData] = useState(null);
  const [youtubeData, setYoutubeData] = useState(null);
  const [loading, setLoading] = useState(true);

  if (!results || !results.topMatch) {
    return (
      <div className="text-center text-[var(--text-primary)]">
        <p>No results to display</p>
        <button onClick={onReset} className="mt-4 px-6 py-3 bg-[var(--accent)] text-white rounded-lg font-semibold">
          Try Again
        </button>
      </div>
    );
  }

  const { topMatch, transcription, audioInfo } = results;

  useEffect(() => {
    fetchMusicData();
  }, [topMatch]);

  const fetchMusicData = async () => {
    setLoading(true);
    try {
      const [spotifyResponse, youtubeResponse] = await Promise.all([
        fetchSpotifyTrack(topMatch.artist, topMatch.title),
        fetchYouTubeVideo(topMatch.artist, topMatch.title)
      ]);
      
      setSpotifyData(spotifyResponse);
      setYoutubeData(youtubeResponse);
    } catch (error) {
      console.error('Error fetching music data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-4 shadow-2xl animate-pulse">
          <Trophy className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-4xl md:text-5xl font-bold text-[var(--text-primary)] mb-3">
          Perfect Match Found!
        </h2>
        <div className="flex items-center justify-center gap-3 mt-4">
          <TierBadge tier={tier} size="lg" />
          <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-full">
            <span className="text-green-500 font-bold text-lg">{Math.round(topMatch.final_score * 100)}% Match</span>
          </div>
        </div>
      </div>

      {/* Main Track Card */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 rounded-3xl blur-3xl animate-pulse" />
        <div className="relative bg-[var(--bg-secondary)] rounded-3xl overflow-hidden border border-[var(--border)] shadow-2xl">
          <div className="grid md:grid-cols-2 gap-0">
            {/* Album Art Section */}
            <div className="relative h-96 bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900 flex items-center justify-center overflow-hidden">
              {loading ? (
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-16 h-16 text-white animate-spin" />
                  <p className="text-white/60">Loading track info...</p>
                </div>
              ) : spotifyData?.image ? (
                <img 
                  src={spotifyData.image} 
                  alt={topMatch.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <>
                  <div className="absolute inset-0 opacity-20">
                    <div className="absolute inset-0" style={{
                      backgroundImage: 'radial-gradient(circle at 30% 50%, rgba(255,255,255,0.15) 0%, transparent 50%)',
                    }} />
                  </div>
                  <Music className="w-32 h-32 text-white/80 relative z-10" />
                </>
              )}
              <div className="absolute bottom-4 right-4 px-4 py-2 bg-black/80 backdrop-blur-sm rounded-full border border-white/20">
                <span className="text-green-400 text-xl font-bold">{Math.round(topMatch.final_score * 100)}%</span>
              </div>
            </div>

            {/* Track Info Section */}
            <div className="p-8 flex flex-col justify-between">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full mb-4">
                  <Trophy className="w-4 h-4 text-yellow-500" />
                  <span className="text-yellow-500 text-sm font-bold uppercase">Best Match</span>
                </div>
                
                <h3 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-3 leading-tight">
                  {topMatch.title}
                </h3>
                <p className="text-2xl text-[var(--text-secondary)] mb-6">{topMatch.artist}</p>
                
                <div className="flex flex-wrap gap-3 mb-6">
                  {topMatch.album && (
                    <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
                      <span className="text-xs text-[var(--text-tertiary)]">Album:</span>
                      <span className="ml-2 text-[var(--text-primary)] font-semibold">{topMatch.album}</span>
                    </div>
                  )}
                  {topMatch.year && (
                    <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
                      <span className="text-xs text-[var(--text-tertiary)]">Year:</span>
                      <span className="ml-2 text-[var(--text-primary)] font-semibold">{topMatch.year}</span>
                    </div>
                  )}
                </div>

                {/* Match Quality Bar */}
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-[var(--text-tertiary)]">Confidence Score</span>
                    <span className="text-lg font-bold text-green-500">Excellent Match</span>
                  </div>
                  <div className="h-3 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-1000"
                      style={{ width: `${topMatch.final_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Streaming Buttons */}
              <div className="space-y-3">
                <StreamingButton
                  platform="spotify"
                  url={spotifyData?.url}
                  loading={loading}
                  artist={topMatch.artist}
                  title={topMatch.title}
                  previewUrl={spotifyData?.preview_url}
                />
                <StreamingButton
                  platform="youtube"
                  url={youtubeData?.url}
                  loading={loading}
                  artist={topMatch.artist}
                  title={topMatch.title}
                  previewUrl={null}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Match Explanation */}
      <MatchExplanation match={topMatch} tier={tier} engine={config?.engine} />

      {/* Lyrics Match */}
      {transcription && topMatch.lyrics_cleaned && (
        <LyricsMatchDisplay
          queryText={transcription}
          songLyrics={topMatch.lyrics_cleaned}
          matchPercentage={topMatch.match_percentage || 0}
        />
      )}

      {/* Audio Info */}
      {audioInfo && (
        <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
          <h3 className="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Audio Analysis
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Sample Rate</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.sample_rate ? `${(audioInfo.sample_rate / 1000).toFixed(1)} kHz` : 'N/A'}
              </p>
            </div>
            
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Duration</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.duration ? `${audioInfo.duration.toFixed(1)}s` : 'N/A'}
              </p>
            </div>
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Engine</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {config?.engine?.toUpperCase() || 'TF-IDF'}
              </p>
            </div>
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Accuracy</p>
              <p className="text-xl font-bold text-green-500">
                {Math.round(topMatch.final_score * 100)}%
              </p>
            </div>

            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Bitrate</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.bitrate ? `${audioInfo.bitrate} kbps` : 'N/A'}
              </p>
            </div>
            
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Channels</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.channels === 2 ? 'Stereo' : 'Mono'}
              </p>
            </div>
            
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">File Size</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.file_size_mb ? `${audioInfo.file_size_mb} MB` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Try Again */}
      <div className="text-center pt-8">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] hover:opacity-90 text-[var(--bg-primary)] font-bold rounded-2xl shadow-2xl transition-all transform hover:scale-105 text-lg"
        >
          <RefreshCw className="w-6 h-6" />
          Analyze Another Song
        </button>
      </div>
    </div>
  );
};