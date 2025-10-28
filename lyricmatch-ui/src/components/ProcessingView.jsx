// src/components/ProcessingView.jsx
import React, { useState, useEffect } from 'react';
import { Loader2, Activity, Cpu, Zap, Radio } from 'lucide-react';
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
    <div className="relative min-h-[90vh] overflow-hidden">
      {/* Fullscreen Background Wave */}
      <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg-primary)] via-indigo-950/20 to-[var(--bg-primary)]">
        <WaveformVisualizer isActive={isProcessing} fullscreen={true} />
      </div>

      {/* Radial Gradient Overlays */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent" />
      
      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_80%)]" />

      {/* Content */}
      <div className="relative z-10 flex items-center justify-center min-h-[90vh] px-6 py-12">
        <div className="w-full max-w-4xl">
          {/* Header Section */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-3 mb-6 flex-wrap justify-center">
              <TierBadge tier={tier} size="lg" />
              {config?.engine && (
                <div className="px-5 py-2.5 bg-[var(--bg-secondary)]/80 backdrop-blur-xl border border-[var(--border)]/50 rounded-full text-sm font-bold text-[var(--text-primary)] shadow-lg">
                  {config.engine.toUpperCase()}
                </div>
              )}
              {config?.use_gpu && (
                <div className="px-5 py-2.5 bg-gradient-to-r from-green-500/20 to-blue-500/20 backdrop-blur-xl border border-green-500/40 rounded-full text-sm font-bold text-green-400 flex items-center gap-2 shadow-lg shadow-green-500/20">
                  <Zap className="w-4 h-4" />
                  GPU Accelerated
                </div>
              )}
            </div>

            {/* Pulsing Radio Icon */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-indigo-500/20 rounded-full blur-2xl animate-pulse" />
                <Radio className="w-16 h-16 text-indigo-400 relative animate-pulse" strokeWidth={1.5} />
              </div>
            </div>

            <h2 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 mb-4 tracking-tight">
              Analyzing Audio
            </h2>
            <p className="text-[var(--text-secondary)] text-lg font-mono mb-2 opacity-80">{filename}</p>
            
            {/* GPU Performance Indicator */}
            {config?.use_gpu && isProcessing && (
              <div className="mt-6 inline-flex items-center gap-3 px-5 py-3 bg-green-500/10 backdrop-blur-xl border border-green-500/30 rounded-2xl shadow-lg shadow-green-500/10">
                <div className="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
                <span className="text-sm text-green-400 font-bold">
                  Processing on GPU • Expected 5-10x speedup
                </span>
              </div>
            )}
          </div>

          {/* Circular Progress */}
          <div className="flex justify-center mb-16">
            <div className="relative w-80 h-80">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse" />
              
              <svg className="w-80 h-80 transform -rotate-90 relative">
                <circle 
                  cx="160" cy="160" r="152" 
                  stroke="currentColor" 
                  strokeWidth="8" 
                  fill="none" 
                  className="text-[var(--border)]/30" 
                />
                <circle
                  cx="160" cy="160" r="152"
                  stroke="url(#progressGradient)"
                  strokeWidth="8" 
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 152}`}
                  strokeDashoffset={`${2 * Math.PI * 152 * (1 - displayProgress / 100)}`}
                  strokeLinecap="round"
                  className="transition-all duration-700 ease-out drop-shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                />
                <defs>
                  <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor={config?.use_gpu ? "#10b981" : "#6366f1"} />
                    <stop offset="50%" stopColor={config?.use_gpu ? "#3b82f6" : "#8b5cf6"} />
                    <stop offset="100%" stopColor={config?.use_gpu ? "#6366f1" : "#a855f7"} />
                  </linearGradient>
                </defs>
              </svg>
              
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                {config?.use_gpu ? (
                  <Zap className="w-24 h-24 text-green-400 mb-4 drop-shadow-[0_0_15px_rgba(34,197,94,0.5)] animate-pulse" strokeWidth={1.5} />
                ) : (
                  <Loader2 className="w-24 h-24 text-indigo-400 animate-spin mb-4 drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]" strokeWidth={1.5} />
                )}
                <div className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 mb-3">
                  {Math.round(displayProgress)}%
                </div>
                <div className="text-[var(--text-secondary)] font-bold text-lg">{currentStage.name}</div>
                {config?.use_gpu && (
                  <div className="mt-3 text-sm text-green-400 font-bold flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    GPU Mode
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Stages Progress */}
          <div className="bg-[var(--bg-secondary)]/50 backdrop-blur-2xl rounded-3xl p-8 border border-[var(--border)]/30 shadow-2xl mb-8">
            <div className="space-y-6">
              {Object.entries(stages).map(([key, stage]) => {
                const isActive = key === status;
                const isCompleted = displayProgress >= stage.minProgress;
                return (
                  <div key={key} className={`flex items-center gap-5 transition-all duration-300 ${isActive ? 'scale-105' : ''}`}>
                    <div className={`w-5 h-5 rounded-full transition-all duration-500 ${
                      isCompleted 
                        ? config?.use_gpu 
                          ? 'bg-gradient-to-r from-green-400 to-blue-500 shadow-lg shadow-green-500/50' 
                          : 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/50' 
                        : 'bg-[var(--border)]'
                    } ${isActive ? 'animate-pulse' : ''}`} />
                    <div className={`flex-1 font-bold text-lg transition-all duration-300 ${
                      isActive 
                        ? 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400' 
                        : isCompleted 
                          ? 'text-[var(--text-secondary)]' 
                          : 'text-[var(--text-tertiary)]'
                    }`}>
                      {stage.name}
                    </div>
                    {isCompleted && !isActive && (
                      <div className="text-green-400 font-bold text-2xl drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]">✓</div>
                    )}
                    {isActive && config?.use_gpu && (
                      <Zap className="w-6 h-6 text-green-400 animate-pulse drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Processing Details */}
          {isProcessing && (
            <div className="bg-[var(--bg-secondary)]/50 backdrop-blur-2xl rounded-3xl p-8 border border-[var(--border)]/30 shadow-2xl">
              <h4 className="text-sm font-black text-[var(--text-secondary)] uppercase tracking-wider mb-6 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Processing Details
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[var(--bg-tertiary)]/50 backdrop-blur-xl rounded-2xl p-4 border border-[var(--border)]/30">
                  <div className="text-xs text-[var(--text-tertiary)] font-semibold uppercase mb-2">Tier</div>
                  <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                    {tier.toUpperCase()}
                  </div>
                </div>
                <div className="bg-[var(--bg-tertiary)]/50 backdrop-blur-xl rounded-2xl p-4 border border-[var(--border)]/30">
                  <div className="text-xs text-[var(--text-tertiary)] font-semibold uppercase mb-2">Engine</div>
                  <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                    {config?.engine?.toUpperCase() || 'N/A'}
                  </div>
                </div>
                <div className="bg-[var(--bg-tertiary)]/50 backdrop-blur-xl rounded-2xl p-4 border border-[var(--border)]/30">
                  <div className="text-xs text-[var(--text-tertiary)] font-semibold uppercase mb-2">Whisper</div>
                  <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                    {config?.whisper_model?.toUpperCase() || 'N/A'}
                  </div>
                </div>
                <div className={`rounded-2xl p-4 ${
                  config?.use_gpu 
                    ? 'bg-gradient-to-br from-green-500/20 to-blue-500/20 border border-green-500/40 shadow-lg shadow-green-500/20' 
                    : 'bg-[var(--bg-tertiary)]/50 backdrop-blur-xl border border-[var(--border)]/30'
                }`}>
                  <div className="text-xs text-[var(--text-tertiary)] font-semibold uppercase mb-2">Device</div>
                  <div className={`text-xl font-black flex items-center gap-2 ${
                    config?.use_gpu 
                      ? 'text-green-400 drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]' 
                      : 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400'
                  }`}>
                    {config?.use_gpu ? (
                      <>
                        <Zap className="w-5 h-5" />
                        GPU
                      </>
                    ) : (
                      <>
                        <Cpu className="w-5 h-5" />
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
    </div>
  );
};