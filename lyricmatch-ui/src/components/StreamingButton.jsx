// src/components/StreamingButton.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

export const StreamingButton = ({ platform, url, loading, artist, title, previewUrl }) => {
  const [showPlayer, setShowPlayer] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(err => {
        console.error('Play failed:', err);
      });
    }
    setIsPlaying(!isPlaying);
  };

  const searchQuery = encodeURIComponent(`${artist} ${title}`);
  const fallbackUrl = platform === 'spotify' 
    ? `https://open.spotify.com/search/${searchQuery}`
    : `https://www.youtube.com/results?search_query=${searchQuery}`;

  const config = {
    spotify: {
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
        </svg>
      ),
      gradient: 'from-green-600 to-green-700 hover:from-green-500 hover:to-green-600',
      name: 'Play on Spotify',
      hasPreview: previewUrl && platform === 'spotify'
    },
    youtube: {
      icon: (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
      ),
      gradient: 'from-red-600 to-red-700 hover:from-red-500 hover:to-red-600',
      name: 'Watch on YouTube',
      hasPreview: false
    }
  };

  const { icon, gradient, name, hasPreview } = config[platform];

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        {/* Preview Button (Spotify only) */}
        {hasPreview && previewUrl && (
          <button
            onClick={togglePlay}
            className={`flex items-center justify-center px-6 py-4 bg-gradient-to-r ${gradient} rounded-xl text-white font-bold transition-all shadow-lg hover:shadow-xl group flex-shrink-0`}
            title={isPlaying ? 'Pause preview' : 'Play 30s preview'}
          >
            {isPlaying ? (
              <div className="flex gap-1">
                <div className="w-1 h-6 bg-white rounded animate-pulse" />
                <div className="w-1 h-6 bg-white rounded animate-pulse" style={{ animationDelay: '0.2s' }} />
              </div>
            ) : (
              <div className="w-0 h-0 border-l-8 border-l-white border-y-6 border-y-transparent ml-1" />
            )}
          </button>
        )}

        {/* Main Link Button */}
        <a
          href={url || fallbackUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`flex-1 flex items-center justify-between px-6 py-4 bg-gradient-to-r ${gradient} rounded-xl text-white font-bold transition-all shadow-lg hover:shadow-xl group ${
            loading ? 'opacity-50 pointer-events-none' : ''
          }`}
        >
          <div className="flex items-center gap-3">
            {icon}
            <span className="text-lg">{name}</span>
          </div>
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <span className="text-2xl group-hover:translate-x-1 transition-transform">→</span>
          )}
        </a>
      </div>

      {/* Audio Player */}
      {hasPreview && previewUrl && (
        <div className="bg-[var(--bg-tertiary)] rounded-lg p-4 border border-[var(--border)]">
          <audio
            ref={audioRef}
            src={previewUrl}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
            className="w-full"
            controls
          />
          <p className="text-xs text-[var(--text-tertiary)] text-center mt-2">
            30-second preview from Spotify
          </p>
        </div>
      )}
    </div>
  );
};