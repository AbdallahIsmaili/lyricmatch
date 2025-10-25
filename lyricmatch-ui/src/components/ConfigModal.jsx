// ============================================
// src/components/ConfigModal.jsx
// ============================================
import React, { useState } from 'react';
import { Settings, Lock, Crown, Star, Rocket, Sparkles, X } from 'lucide-react';
import { TierBadge } from './TierBadge';

export const ConfigModal = ({ isOpen, onClose, onStart, currentTier, onChangeTier }) => {
  const [config, setConfig] = useState({
    whisper_model: 'tiny',
    engine: 'tfidf',
    sbert_model: 'all-MiniLM-L6-v2'
  });

  const tiers = {
    free: {
      whisper: ['tiny', 'base'],
      engines: ['tfidf'],
      sbert: []
    },
    premium: {
      whisper: ['tiny', 'base', 'small', 'medium', 'large'],
      engines: ['tfidf', 'neural', 'hybrid'],
      sbert: ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'paraphrase-MiniLM-L6-v2']
    }
  };

  const whisperInfo = {
    tiny: { speed: 'Fastest', accuracy: 'Basic', size: '39M' },
    base: { speed: 'Fast', accuracy: 'Good', size: '74M' },
    small: { speed: 'Medium', accuracy: 'Better', size: '244M' },
    medium: { speed: 'Slow', accuracy: 'Great', size: '769M' },
    large: { speed: 'Slowest', accuracy: 'Best', size: '1550M' }
  };

  const engineInfo = {
    tfidf: { name: 'TF-IDF', description: 'Fast keyword-based matching', accuracy: 'Good' },
    neural: { name: 'Neural (BERT)', description: 'Advanced semantic understanding', accuracy: 'Excellent' },
    hybrid: { name: 'Hybrid', description: 'Combined TF-IDF + Neural', accuracy: 'Best' }
  };

  const sbertInfo = {
    'all-MiniLM-L6-v2': { speed: 'Fast', quality: 'Good', dims: '384' },
    'all-mpnet-base-v2': { speed: 'Medium', quality: 'Best', dims: '768' },
    'paraphrase-MiniLM-L6-v2': { speed: 'Fast', quality: 'Good', dims: '384' }
  };

  if (!isOpen) return null;

  const tierConfig = tiers[currentTier];
  const isLocked = (value, list) => !list.includes(value);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-[var(--border)] flex items-center justify-between bg-gradient-to-r from-[var(--bg-secondary)] to-transparent">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-[var(--text-primary)]" />
            <h2 className="text-2xl font-bold text-[var(--text-primary)]">Configuration</h2>
            <TierBadge tier={currentTier} size="lg" />
          </div>
          <button onClick={onClose} className="px-4 py-2 text-sm bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] text-[var(--text-primary)] rounded-lg transition-colors">
            Close
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-200px)] p-6">
          {currentTier === 'free' && (
            <div className="mb-6 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <Crown className="w-8 h-8 text-yellow-500 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">Unlock Premium Features</h3>
                  <p className="text-[var(--text-secondary)] mb-4">Get access to advanced AI models, neural embeddings, and unlimited searches</p>
                  <button
                    onClick={() => { onChangeTier('premium'); onClose(); }}
                    className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-bold rounded-lg shadow-lg hover:shadow-yellow-500/50 transition-all"
                  >
                    Upgrade to Premium
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Whisper Model Selection */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <Rocket className="w-5 h-5" />
              Speech Recognition Model
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(whisperInfo).map(([model, info]) => {
                const locked = isLocked(model, tierConfig.whisper);
                return (
                  <button
                    key={model}
                    onClick={() => !locked && setConfig(prev => ({ ...prev, whisper_model: model }))}
                    disabled={locked}
                    className={`relative p-4 rounded-xl border-2 text-left transition-all ${
                      config.whisper_model === model
                        ? 'border-[var(--accent)] bg-[var(--accent)]/5'
                        : locked
                        ? 'border-[var(--border)] bg-[var(--bg-secondary)]/30 opacity-50 cursor-not-allowed'
                        : 'border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)]/50'
                    }`}
                  >
                    {locked && (
                      <div className="absolute top-3 right-3">
                        <Lock className="w-5 h-5 text-yellow-500" />
                      </div>
                    )}
                    <div className="font-bold text-[var(--text-primary)] text-lg mb-2 uppercase">{model}</div>
                    <div className="text-sm space-y-1">
                      <div className="flex justify-between text-[var(--text-secondary)]">
                        <span>Speed:</span>
                        <span className="font-semibold">{info.speed}</span>
                      </div>
                      <div className="flex justify-between text-[var(--text-secondary)]">
                        <span>Accuracy:</span>
                        <span className="font-semibold">{info.accuracy}</span>
                      </div>
                      <div className="flex justify-between text-[var(--text-tertiary)]">
                        <span>Size:</span>
                        <span className="font-mono text-xs">{info.size}</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Matching Engine Selection */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Matching Algorithm
            </h3>
            <div className="space-y-3">
              {Object.entries(engineInfo).map(([engine, info]) => {
                const locked = isLocked(engine, tierConfig.engines);
                return (
                  <button
                    key={engine}
                    onClick={() => !locked && setConfig(prev => ({ ...prev, engine }))}
                    disabled={locked}
                    className={`relative w-full p-5 rounded-xl border-2 text-left transition-all ${
                      config.engine === engine
                        ? 'border-[var(--accent)] bg-[var(--accent)]/5'
                        : locked
                        ? 'border-[var(--border)] bg-[var(--bg-secondary)]/30 opacity-50 cursor-not-allowed'
                        : 'border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)]/50'
                    }`}
                  >
                    {locked && (
                      <div className="absolute top-4 right-4 flex items-center gap-2">
                        <span className="text-xs font-bold text-yellow-500 uppercase">Premium</span>
                        <Lock className="w-5 h-5 text-yellow-500" />
                      </div>
                    )}
                    <div className="font-bold text-[var(--text-primary)] text-xl mb-2">{info.name}</div>
                    <div className="text-[var(--text-secondary)] mb-3">{info.description}</div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-[var(--bg-tertiary)] rounded-full text-sm">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="text-[var(--text-primary)] font-semibold">{info.accuracy}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* SBERT Model Selection */}
          {(config.engine === 'neural' || config.engine === 'hybrid') && (
            <div className="mb-8">
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                <Crown className="w-5 h-5 text-yellow-500" />
                Neural Model (BERT)
              </h3>
              <div className="space-y-3">
                {Object.entries(sbertInfo).map(([model, info]) => {
                  const locked = isLocked(model, tierConfig.sbert);
                  return (
                    <button
                      key={model}
                      onClick={() => !locked && setConfig(prev => ({ ...prev, sbert_model: model }))}
                      disabled={locked}
                      className={`relative w-full p-4 rounded-xl border-2 text-left transition-all ${
                        config.sbert_model === model
                          ? 'border-[var(--accent)] bg-[var(--accent)]/5'
                          : locked
                          ? 'border-[var(--border)] bg-[var(--bg-secondary)]/30 opacity-50 cursor-not-allowed'
                          : 'border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)]/50'
                      }`}
                    >
                      {locked && (
                        <div className="absolute top-3 right-3">
                          <Lock className="w-5 h-5 text-yellow-500" />
                        </div>
                      )}
                      <div className="font-mono text-[var(--text-primary)] font-semibold mb-2">{model}</div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-[var(--text-tertiary)]">Speed:</span>
                          <span className="ml-2 text-[var(--text-primary)] font-semibold">{info.speed}</span>
                        </div>
                        <div>
                          <span className="text-[var(--text-tertiary)]">Quality:</span>
                          <span className="ml-2 text-[var(--text-primary)] font-semibold">{info.quality}</span>
                        </div>
                        <div>
                          <span className="text-[var(--text-tertiary)]">Dims:</span>
                          <span className="ml-2 text-[var(--text-primary)] font-semibold">{info.dims}</span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-[var(--border)] bg-[var(--bg-secondary)]">
          <button
            onClick={() => onStart(config)}
            className="w-full px-8 py-4 bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] text-[var(--bg-primary)] font-bold rounded-xl shadow-lg hover:shadow-xl transition-all text-lg"
          >
            Start Processing
          </button>
        </div>
      </div>
    </div>
  );
};