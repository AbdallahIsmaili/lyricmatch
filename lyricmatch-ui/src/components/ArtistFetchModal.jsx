// src/components/ArtistFetchModal.jsx
import React, { useState, useEffect } from 'react';
import { Music, Loader2, Database, Check, X, Sparkles, Radio, Download, Search, TrendingUp, Crown, AlertCircle } from 'lucide-react';
import { fetchArtistSongs } from '../utils/api';

export const ArtistFetchModal = ({ isOpen, onClose, onFetch }) => {
  const [artistName, setArtistName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('idle'); // idle, searching, fetching, processing, complete, error
  const [stats, setStats] = useState({ songs: 0, albums: 0, duration: 0 });
  const [error, setError] = useState(null);
  const [existingArtists, setExistingArtists] = useState([]);
  const [suggestedArtists, setSuggestedArtists] = useState([
    'Travis Scott', 'Kendrick Lamar', 'SZA', 'Bad Bunny', 
    'Olivia Rodrigo', 'Doja Cat', 'Post Malone', '21 Savage'
  ]);

  // Load existing artists from database
  useEffect(() => {
    if (isOpen) {
      loadExistingArtists();
    }
  }, [isOpen]);

  const loadExistingArtists = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats');
      const data = await response.json();
      if (data.top_artists) {
        const artists = data.top_artists.map(([name]) => name.toLowerCase());
        setExistingArtists(artists);
      }
    } catch (err) {
      console.error('Failed to load existing artists:', err);
    }
  };

  useEffect(() => {
    if (!isOpen) {
      // Reset state when modal closes
      setTimeout(() => {
        setArtistName('');
        setLoading(false);
        setStatus('');
        setProgress(0);
        setStage('idle');
        setStats({ songs: 0, albums: 0, duration: 0 });
        setError(null);
      }, 300);
    }
  }, [isOpen]);

  // Animated progress for visual feedback
  useEffect(() => {
    if (loading && stage !== 'complete' && stage !== 'error') {
      const interval = setInterval(() => {
        setProgress(prev => {
          const increment = Math.random() * 10 + 3;
          const newProgress = Math.min(prev + increment, 85);
          return newProgress;
        });
      }, 800);
      return () => clearInterval(interval);
    }
  }, [loading, stage]);

  const checkArtistExists = (name) => {
    return existingArtists.includes(name.toLowerCase().trim());
  };

  const handleArtistNameChange = (value) => {
    setArtistName(value);
    setError(null);
    
    // Check if artist already exists
    if (value.trim() && checkArtistExists(value)) {
      setError('This artist is already in the database');
    }
  };

  const handleFetch = async () => {
    if (!artistName.trim()) return;
    
    // Check if artist already exists
    if (checkArtistExists(artistName)) {
      setError('This artist is already in the database');
      return;
    }
    
    setLoading(true);
    setProgress(0);
    setError(null);
    setStage('searching');
    setStatus('Searching for artist on Genius...');
    
    const startTime = Date.now();
    
    try {
      // Actual API call
      setStage('fetching');
      setStatus('Fetching songs from Genius API...');
      setProgress(30);
      
      const data = await fetchArtistSongs(artistName);
      
      setStage('processing');
      setStatus('Processing lyrics and rebuilding indexes...');
      setProgress(70);
      
      // Wait a bit for backend processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const duration = ((Date.now() - startTime) / 1000).toFixed(1);
      
      setStats({
        songs: data.songs_added || 0,
        albums: Math.floor((data.songs_added || 0) / 5), // Rough estimate
        duration: duration
      });
      
      setProgress(100);
      setStage('complete');
      setStatus(`Successfully added ${data.songs_added} songs for ${data.artist}!`);
      
      setTimeout(() => {
        onFetch();
        onClose();
      }, 2500);
    } catch (err) {
      setStage('error');
      setStatus(err.message || 'Failed to fetch artist data');
      setProgress(0);
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && artistName.trim() && !loading && !error) {
      handleFetch();
    }
  };

  if (!isOpen) return null;

  const artistExists = checkArtistExists(artistName);
  const isInputInvalid = artistName.trim() && artistExists;

  // Filter suggested artists to show only ones NOT in database
  const filteredSuggestions = suggestedArtists.filter(
    artist => !checkArtistExists(artist)
  );

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-3xl max-w-2xl w-full overflow-hidden shadow-2xl animate-in slide-in-from-bottom-4 duration-300">
        
        {/* Header with gradient */}
        <div className="relative bg-gradient-to-br from-purple-500/10 via-blue-500/10 to-pink-500/10 border-b border-[var(--border)] p-8">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMDMpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />
          
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/50">
                  <Database className="w-8 h-8 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center shadow-lg">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              </div>
              <div>
                <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-1">
                  Add Artist to Database
                </h2>
                <p className="text-[var(--text-secondary)]">Fetch songs from Genius API</p>
              </div>
            </div>
            {!loading && (
              <button
                onClick={onClose}
                className="w-10 h-10 flex items-center justify-center rounded-xl bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] transition-colors border border-[var(--border)]"
              >
                <X className="w-5 h-5 text-[var(--text-primary)]" />
              </button>
            )}
          </div>
        </div>

        <div className="p-8">
          {/* Input Section */}
          {stage === 'idle' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-top-2 duration-500">
              <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2">
                  <Search className="w-5 h-5 text-[var(--text-tertiary)]" />
                </div>
                <input
                  type="text"
                  value={artistName}
                  onChange={(e) => handleArtistNameChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter artist name (e.g., Taylor Swift, Drake...)"
                  className={`w-full pl-12 pr-4 py-4 bg-[var(--bg-secondary)] border-2 ${
                    isInputInvalid 
                      ? 'border-red-500 focus:border-red-500' 
                      : 'border-[var(--border)] focus:border-purple-500'
                  } rounded-xl text-[var(--text-primary)] text-lg placeholder:text-[var(--text-tertiary)] transition-all outline-none`}
                  disabled={loading}
                  autoFocus
                />
                {isInputInvalid && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  </div>
                )}
              </div>

              {/* Error message */}
              {error && (
                <div className="bg-red-500/10 border-2 border-red-500 rounded-xl p-4 flex items-center gap-3 animate-in slide-in-from-top-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-red-500 font-semibold">{error}</p>
                </div>
              )}

              {/* Quick suggestions - filtered */}
              {filteredSuggestions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  <span className="text-xs text-[var(--text-tertiary)] font-semibold uppercase tracking-wide">
                    Suggested (not in database):
                  </span>
                  {filteredSuggestions.map(artist => (
                    <button
                      key={artist}
                      onClick={() => handleArtistNameChange(artist)}
                      className="px-3 py-1 bg-[var(--bg-tertiary)] hover:bg-purple-500/20 border border-[var(--border)] hover:border-purple-500/50 rounded-full text-xs font-medium text-[var(--text-secondary)] hover:text-purple-400 transition-all"
                    >
                      {artist}
                    </button>
                  ))}
                </div>
              )}

              <button
                onClick={handleFetch}
                disabled={loading || !artistName.trim() || isInputInvalid}
                className="w-full px-8 py-4 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold rounded-xl shadow-lg hover:shadow-purple-500/50 disabled:shadow-none transition-all text-lg flex items-center justify-center gap-3 group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-5 h-5 group-hover:animate-bounce" />
                Fetch Artist Data
              </button>
            </div>
          )}

          {/* Loading/Processing State */}
          {(loading || stage !== 'idle') && stage !== 'complete' && stage !== 'error' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Animated Artist Card */}
              <div className="relative bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-2xl p-6 border border-purple-500/30 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 animate-pulse" />
                <div className="relative flex items-center gap-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-xl animate-pulse">
                    <Music className="w-10 h-10 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-1">{artistName}</h3>
                    <p className="text-purple-400 font-semibold">{status}</p>
                  </div>
                  <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-[var(--text-secondary)]">Processing</span>
                  <span className="text-sm font-bold text-purple-500">{Math.round(progress)}%</span>
                </div>
                <div className="h-3 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 rounded-full transition-all duration-500 ease-out relative"
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute inset-0 bg-white/30 animate-pulse" />
                  </div>
                </div>
              </div>

              {/* Stage Indicators */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: 'searching', icon: Search, label: 'Searching', color: 'blue' },
                  { id: 'fetching', icon: Radio, label: 'Fetching', color: 'purple' },
                  { id: 'processing', icon: TrendingUp, label: 'Processing', color: 'pink' }
                ].map(({ id, icon: Icon, label, color }) => (
                  <div
                    key={id}
                    className={`relative p-4 rounded-xl border-2 transition-all duration-300 ${
                      stage === id
                        ? `border-${color}-500 bg-${color}-500/10`
                        : progress > 0
                        ? 'border-green-500/50 bg-green-500/5'
                        : 'border-[var(--border)] bg-[var(--bg-secondary)]'
                    }`}
                  >
                    <Icon className={`w-6 h-6 mx-auto mb-2 ${
                      stage === id
                        ? `text-${color}-500 animate-pulse`
                        : progress > 0
                        ? 'text-green-500'
                        : 'text-[var(--text-tertiary)]'
                    }`} />
                    <p className={`text-xs font-semibold text-center ${
                      stage === id
                        ? `text-${color}-500`
                        : progress > 0
                        ? 'text-green-500'
                        : 'text-[var(--text-tertiary)]'
                    }`}>
                      {label}
                    </p>
                    {stage === id && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Success State */}
          {stage === 'complete' && (
            <div className="space-y-6 animate-in fade-in zoom-in duration-500">
              <div className="relative bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-2xl p-8 border border-green-500/30 text-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-emerald-500/5 animate-pulse" />
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl shadow-green-500/50 animate-bounce">
                    <Check className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Success!</h3>
                  <p className="text-lg text-green-500 font-semibold mb-6">{status}</p>
                  
                  {/* Stats Grid */}
                  <div className="grid grid-cols-3 gap-4 mt-6">
                    <div className="bg-[var(--bg-secondary)] rounded-xl p-4 border border-[var(--border)]">
                      <Music className="w-6 h-6 text-green-500 mx-auto mb-2" />
                      <p className="text-3xl font-bold text-[var(--text-primary)]">{stats.songs}</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Songs Added</p>
                    </div>
                    <div className="bg-[var(--bg-secondary)] rounded-xl p-4 border border-[var(--border)]">
                      <Crown className="w-6 h-6 text-purple-500 mx-auto mb-2" />
                      <p className="text-3xl font-bold text-[var(--text-primary)]">{stats.albums}</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Albums</p>
                    </div>
                    <div className="bg-[var(--bg-secondary)] rounded-xl p-4 border border-[var(--border)]">
                      <Loader2 className="w-6 h-6 text-blue-500 mx-auto mb-2" />
                      <p className="text-3xl font-bold text-[var(--text-primary)]">{stats.duration}s</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Duration</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {stage === 'error' && (
            <div className="space-y-6 animate-in fade-in shake duration-500">
              <div className="bg-gradient-to-br from-red-500/10 to-rose-500/10 rounded-2xl p-8 border border-red-500/30 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-rose-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl shadow-red-500/50">
                  <X className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Error</h3>
                <p className="text-red-400 font-semibold mb-6">{status}</p>
                <button
                  onClick={() => setStage('idle')}
                  className="px-6 py-3 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-400 font-semibold rounded-xl transition-all"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};