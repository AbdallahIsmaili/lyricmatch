// src/components/ProcessingView.jsx
import React, { useState, useEffect } from 'react';
import { Loader2, Activity } from 'lucide-react';
import { TierBadge } from './TierBadge';
import { WaveformVisualizer } from './WaveformVisualizer';

export const ProcessingView = ({ progress, filename, status, tier, config }) => {
  const [displayProgress, setDisplayProgress] = useState(0);
  
  useEffect(() => {
    const safeProgress = Math.min(100, Math.max(0, parseInt(progress) || 0));
    setDisplayProgress(prev => Math.max(prev, safeProgress));
  }, [progress]);
  
  const stages = {
    'queued': { name: 'Queued', minProgress: 0 },
    'preprocessing': { name: 'Preprocessing Audio', minProgress: 10 },
    'transcribing': { name: `Transcribing (${config?.whisper_model || 'base'})`, minProgress: 30 },
    'matching': { name: `Matching (${config?.engine || 'tfidf'})`, minProgress: 70 },
    'complete': { name: 'Complete!', minProgress: 100 }
  };

  const currentStage = stages[status] || stages['queued'];
  const isProcessing = status !== 'queued' && status !== 'complete';

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <TierBadge tier={tier} size="lg" />
            {config?.engine && (
              <div className="px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-full text-sm font-semibold text-[var(--text-primary)]">
                {config.engine.toUpperCase()}
              </div>
            )}
          </div>
          <h2 className="text-4xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">Analyzing Audio</h2>
          <p className="text-[var(--text-secondary)] text-lg font-mono">{filename}</p>
        </div>

        <div className="mb-8 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-[var(--text-primary)]" />
            <span className="text-sm font-semibold text-[var(--text-primary)]">Audio Waveform</span>
          </div>
          <WaveformVisualizer isActive={isProcessing} />
        </div>

        <div className="flex justify-center mb-12">
          <div className="relative w-72 h-72">
            <svg className="w-72 h-72 transform -rotate-90">
              <circle cx="144" cy="144" r="136" stroke="currentColor" strokeWidth="12" fill="none" className="text-[var(--border)]" />
              <circle
                cx="144" cy="144" r="136"
                stroke="url(#gradient)"
                strokeWidth="12" fill="none"
                strokeDasharray={`${2 * Math.PI * 136}`}
                strokeDashoffset={`${2 * Math.PI * 136 * (1 - displayProgress / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-500 ease-out"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--accent)" />
                  <stop offset="100%" stopColor="var(--accent-secondary)" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Loader2 className="w-20 h-20 text-[var(--text-primary)] animate-spin mb-4" />
              <div className="text-6xl font-bold text-[var(--text-primary)] mb-2">{Math.round(displayProgress)}%</div>
              <div className="text-[var(--text-secondary)] font-semibold">{currentStage.name}</div>
            </div>
          </div>
        </div>

        <div className="bg-[var(--bg-secondary)] rounded-2xl p-8 border border-[var(--border)]">
          <div className="space-y-5">
            {Object.entries(stages).map(([key, stage]) => {
              const isActive = key === status;
              const isCompleted = displayProgress >= stage.minProgress;
              return (
                <div key={key} className={`flex items-center gap-4 transition-all ${isActive ? 'scale-105' : ''}`}>
                  <div className={`w-4 h-4 rounded-full transition-all ${isCompleted ? 'bg-[var(--accent)]' : 'bg-[var(--border)]'} ${isActive ? 'animate-pulse' : ''}`} />
                  <div className={`flex-1 font-medium text-lg ${isActive ? 'text-[var(--text-primary)]' : isCompleted ? 'text-[var(--text-secondary)]' : 'text-[var(--text-tertiary)]'}`}>
                    {stage.name}
                  </div>
                  {isCompleted && !isActive && <div className="text-[var(--accent)] font-bold text-xl">✓</div>}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};