// src/components/Header.jsx
import React, { useState } from 'react';
import { Music, History, Sun, Moon, Plus } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { TierBadge } from './TierBadge';
import { HistoryModal } from './HistoryModal';

export const Header = ({ currentTier, onChangeTier, setShowArtistFetch }) => {
  const [showHistory, setShowHistory] = useState(false);
  const { theme, toggleTheme } = useTheme();

  return (
    <>  
      <header className="border-b border-[var(--border)] backdrop-blur-xl bg-[var(--bg-header)] sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 bg-gradient-to-br from-gray-900 to-black rounded-xl flex items-center justify-center border border-[var(--border)] shadow-lg">
              <Music className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">WaveSeek</h1>
              <div className="h-0.5 w-full bg-gradient-to-r from-[var(--accent)] to-transparent" />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowHistory(true)}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors border border-[var(--border)]"
            >
              <History className="w-4 h-4 text-[var(--text-primary)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">History</span>
            </button>
            <button
              onClick={onChangeTier}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors border border-[var(--border)]"
            >
              <TierBadge tier={currentTier} />
              <span className="text-sm font-medium text-[var(--text-secondary)]">Change</span>
            </button>
            <button
              onClick={toggleTheme}
              className="w-10 h-10 flex items-center justify-center bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors border border-[var(--border)]"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5 text-[var(--text-primary)]" /> : <Moon className="w-5 h-5 text-[var(--text-primary)]" />}
            </button>
            <button
              onClick={() => setShowArtistFetch(true)}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors border border-[var(--border)]"
            >
              <Plus className="w-5 h-5 text-[var(--text-primary)]" />
              <span className="text-sm text-[var(--text-primary)]">Add Artist</span>
            </button>
          </div>
        </div>
      </header>
      <HistoryModal 
        isOpen={showHistory} 
        onClose={() => setShowHistory(false)}
        onSelectItem={(item) => {
          console.log('Selected history item:', item);
        }}
      />
    </>
  );
};