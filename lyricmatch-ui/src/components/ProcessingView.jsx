// src/components/ProcessingView.jsx
import React, { useState, useEffect } from 'react';
import { Loader2, Activity, Cpu, Zap } from 'lucide-react';
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
          <div className="inline-flex items-center gap-2 mb-4 flex-wrap justify-center">
            <TierBadge tier={tier} size="lg" />
            {config?.engine && (
              <div className="px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-full text-sm font-semibold text-[var(--text-primary)]">
                {config.engine.toUpperCase()}
              </div>
            )}
            {config?.use_gpu && (
              <div className="px-4 py-2 bg-gradient-to-r from-green-500/20 to-blue-500/20 border border-green-500/30 rounded-full text-sm font-bold text-green-500 flex items-center gap-2 animate-pulse-slow">
                <Zap className="w-4 h-4" />
                GPU Accelerated
              </div>
            )}
            {config?.whisper_model && (
              <div className="px-3 py-1 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-full text-xs font-semibold text-[var(--text-secondary)]">
                Whisper: {config.whisper_model.toUpperCase()}
              </div>
            )}
          </div>
          <h2 className="text-4xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">
            Analyzing Audio
          </h2>
          <p className="text-[var(--text-secondary)] text-lg font-mono">{filename}</p>
          
          {/* GPU Performance Indicator */}
          {config?.use_gpu && isProcessing && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-500 font-semibold">
                Processing on GPU • Expected 5-10x speedup
              </span>
            </div>
          )}
        </div>

        <div className="mb-8 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-[var(--text-primary)]" />
            <span className="text-sm font-semibold text-[var(--text-primary)]">Audio Waveform</span>
            {config?.use_gpu && (
              <span className="ml-auto text-xs text-green-500 font-bold flex items-center gap-1">
                <Zap className="w-3 h-3" />
                GPU
              </span>
            )}
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
                  <stop offset="0%" stopColor={config?.use_gpu ? "#10b981" : "var(--accent)"} />
                  <stop offset="100%" stopColor={config?.use_gpu ? "#3b82f6" : "var(--accent-secondary)"} />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              {config?.use_gpu ? (
                <Zap className="w-20 h-20 text-green-500 animate-pulse mb-4" />
              ) : (
                <Loader2 className="w-20 h-20 text-[var(--text-primary)] animate-spin mb-4" />
              )}
              <div className="text-6xl font-bold text-[var(--text-primary)] mb-2">{Math.round(displayProgress)}%</div>
              <div className="text-[var(--text-secondary)] font-semibold">{currentStage.name}</div>
              {config?.use_gpu && (
                <div className="mt-2 text-xs text-green-500 font-bold">⚡ GPU Mode</div>
              )}
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
                  <div className={`w-4 h-4 rounded-full transition-all ${
                    isCompleted 
                      ? config?.use_gpu 
                        ? 'bg-gradient-to-r from-green-500 to-blue-500' 
                        : 'bg-[var(--accent)]' 
                      : 'bg-[var(--border)]'
                  } ${isActive ? 'animate-pulse' : ''}`} />
                  <div className={`flex-1 font-medium text-lg ${isActive ? 'text-[var(--text-primary)]' : isCompleted ? 'text-[var(--text-secondary)]' : 'text-[var(--text-tertiary)]'}`}>
                    {stage.name}
                  </div>
                  {isCompleted && !isActive && <div className="text-[var(--accent)] font-bold text-xl">✓</div>}
                  {isActive && config?.use_gpu && (
                    <Zap className="w-5 h-5 text-green-500 animate-pulse" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Processing Details */}
        {isProcessing && (
          <div className="mt-6 bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border)]">
            <h4 className="text-sm font-bold text-[var(--text-secondary)] uppercase mb-4">Processing Details</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[var(--bg-tertiary)] rounded-lg p-3">
                <div className="text-xs text-[var(--text-tertiary)] mb-1">Tier</div>
                <div className="text-lg font-bold text-[var(--text-primary)]">{tier.toUpperCase()}</div>
              </div>
              <div className="bg-[var(--bg-tertiary)] rounded-lg p-3">
                <div className="text-xs text-[var(--text-tertiary)] mb-1">Engine</div>
                <div className="text-lg font-bold text-[var(--text-primary)]">{config?.engine?.toUpperCase() || 'N/A'}</div>
              </div>
              <div className="bg-[var(--bg-tertiary)] rounded-lg p-3">
                <div className="text-xs text-[var(--text-tertiary)] mb-1">Whisper</div>
                <div className="text-lg font-bold text-[var(--text-primary)]">{config?.whisper_model?.toUpperCase() || 'N/A'}</div>
              </div>
              <div className={`rounded-lg p-3 ${config?.use_gpu ? 'bg-gradient-to-br from-green-500/20 to-blue-500/20 border border-green-500/30' : 'bg-[var(--bg-tertiary)]'}`}>
                <div className="text-xs text-[var(--text-tertiary)] mb-1">Device</div>
                <div className={`text-lg font-bold flex items-center gap-1 ${config?.use_gpu ? 'text-green-500' : 'text-[var(--text-primary)]'}`}>
                  {config?.use_gpu ? (
                    <>
                      <Zap className="w-4 h-4" />
                      GPU
                    </>
                  ) : (
                    <>
                      <Cpu className="w-4 h-4" />
                      CPU
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};