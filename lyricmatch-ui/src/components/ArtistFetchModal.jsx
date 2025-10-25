// src/components/ArtistFetchModal.jsx
import React, { useState } from 'react';
import { fetchArtistSongs } from '../utils/api';

export const ArtistFetchModal = ({ isOpen, onClose, onFetch }) => {
  const [artistName, setArtistName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  const handleFetch = async () => {
    if (!artistName.trim()) return;
    
    setLoading(true);
    setStatus('Fetching songs...');
    
    try {
      const data = await fetchArtistSongs(artistName);
      setStatus(`✅ Added ${data.songs_added} songs for ${data.artist}`);
      setTimeout(() => {
        onFetch();
        onClose();
      }, 2000);
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-2xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-4">
          Add Artist to Database
        </h2>
        <input
          type="text"
          value={artistName}
          onChange={(e) => setArtistName(e.target.value)}
          placeholder="Enter artist name..."
          className="w-full px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] mb-4"
          disabled={loading}
        />
        {status && (
          <div className="mb-4 p-3 bg-[var(--bg-secondary)] rounded-lg text-sm">
            {status}
          </div>
        )}
        <div className="flex gap-3">
          <button
            onClick={handleFetch}
            disabled={loading || !artistName.trim()}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] text-[var(--bg-primary)] font-bold rounded-lg disabled:opacity-50"
          >
            {loading ? 'Fetching...' : 'Fetch Songs'}
          </button>
          <button
            onClick={onClose}
            disabled={loading}
            className="px-6 py-3 bg-[var(--bg-secondary)] text-[var(--text-primary)] font-bold rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};