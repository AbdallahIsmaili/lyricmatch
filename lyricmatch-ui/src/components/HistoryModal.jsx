// src/components/HistoryModal.jsx
import React, { useState, useEffect } from 'react';
import { History, Loader2, X, Trophy } from 'lucide-react';
import { getHistory, clearHistory } from '../utils/db';
import { TierBadge } from './TierBadge';

export const HistoryModal = ({ isOpen, onClose, onSelectItem }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const items = await getHistory(20);
      setHistory(items);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      await clearHistory();
      setHistory([]);
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-[var(--border)] flex items-center justify-between bg-gradient-to-r from-[var(--bg-secondary)] to-transparent">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6 text-[var(--text-primary)]" />
            <h2 className="text-2xl font-bold text-[var(--text-primary)]">Search History</h2>
            <div className="px-3 py-1 bg-[var(--bg-tertiary)] rounded-full text-sm font-bold text-[var(--text-secondary)]">
              {history.length}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {history.length > 0 && (
              <button
                onClick={handleClearHistory}
                className="px-4 py-2 text-sm bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg transition-colors font-semibold"
              >
                Clear All
              </button>
            )}
            <button 
              onClick={onClose} 
              className="p-2 hover:bg-[var(--bg-secondary)] rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-[var(--text-primary)]" />
            </button>
          </div>
        </div>

        <div className="overflow-y-auto max-h-[60vh] p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 text-[var(--text-secondary)] animate-spin mb-4" />
              <p className="text-[var(--text-secondary)]">Loading history...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12 text-[var(--text-secondary)]">
              <History className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p className="text-lg font-semibold mb-2">No search history yet</p>
              <p className="text-sm">Your searches will appear here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="group bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-4 hover:bg-[var(--bg-tertiary)] hover:border-[var(--accent)]/50 transition-all cursor-pointer"
                  onClick={() => {
                    onSelectItem(item);
                    onClose();
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-[var(--text-primary)] text-lg">
                          {item.topMatch?.title || 'Unknown'}
                        </h3>
                        <TierBadge tier={item.tier || 'free'} />
                      </div>
                      <p className="text-[var(--text-secondary)]">
                        {item.topMatch?.artist || 'Unknown Artist'}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-4">
                      <div className="inline-flex items-center gap-1 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full mb-1">
                        <Trophy className="w-4 h-4 text-green-500" />
                        <span className="text-lg font-bold text-green-500">
                          {Math.round((item.topMatch?.final_score || 0) * 100)}%
                        </span>
                      </div>
                      <div className="text-xs text-[var(--text-tertiary)]">
                        {formatDate(item.timestamp)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 text-xs">
                    <div className="px-2 py-1 bg-[var(--bg-tertiary)] rounded text-[var(--text-secondary)] font-mono">
                      {item.filename || 'Unknown file'}
                    </div>
                    {item.config?.engine && (
                      <div className="px-2 py-1 bg-blue-500/10 border border-blue-500/30 rounded text-blue-500 font-semibold uppercase">
                        {item.config.engine}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-[var(--border)] bg-[var(--bg-secondary)] text-center text-sm text-[var(--text-tertiary)]">
          History is stored locally in your browser
        </div>
      </div>
    </div>
  );
};