// ============================================
// src/components/ConfigModal.jsx - Professional SaaS Design
// ============================================
import React, { useEffect, useState } from 'react';
import { Settings, Lock, Crown, Rocket, Sparkles, X, Loader2, Zap, Cpu, ChevronRight, Check, Info, Gauge, Clock, Activity } from 'lucide-react';

// Mock API for demo
const getGPUStatus = async () => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        available: true,
        name: 'NVIDIA RTX 3060',
        memory_total_gb: 12,
        memory_free_gb: 10.5,
        temperature_c: 45,
        temp_safe: true
      });
    }, 1000);
  });
};

const TierBadge = ({ tier, size = 'sm' }) => {
  const isPremium = tier === 'premium';
  const sizeClasses = size === 'lg' ? 'px-4 py-2 text-base' : 'px-3 py-1.5 text-xs';
  
  return (
    <div className={`inline-flex items-center gap-1.5 ${sizeClasses} rounded-lg font-bold uppercase tracking-wider transition-all ${
      isPremium 
        ? 'bg-gradient-to-r from-amber-500 via-orange-500 to-amber-500 text-white shadow-lg shadow-amber-500/25' 
        : 'bg-slate-800 text-slate-300 border border-slate-700'
    }`}>
      {isPremium ? <Crown className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} /> : <Zap className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />}
      <span>{tier === 'premium' ? 'Premium' : 'Free'}</span>
    </div>
  );
};

export const ConfigModal = ({ isOpen = true, onClose = () => {}, onStart = () => {}, currentTier = 'premium', onChangeTier = () => {} }) => {
  const [gpuStatus, setGpuStatus] = useState(null);
  const [loadingGPU, setLoadingGPU] = useState(true);
  const [activeSection, setActiveSection] = useState(null);

  useEffect(() => {
    if (isOpen && currentTier === 'premium') {
      fetchGPUStatus();
    }
  }, [isOpen, currentTier]);

  const fetchGPUStatus = async () => {
    setLoadingGPU(true);
    try {
      const status = await getGPUStatus();
      setGpuStatus(status);
    } catch (error) {
      console.error('Failed to fetch GPU status:', error);
      setGpuStatus({ available: false });
    } finally {
      setLoadingGPU(false);
    }
  };

  const [config, setConfig] = useState({
    whisper_model: 'base',
    engine: 'hybrid',
    sbert_model: 'all-MiniLM-L6-v2',
    use_gpu: true
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
    tiny: { speed: '~32x', accuracy: 'Basic', size: '39M', time: '2-5s' },
    base: { speed: '~16x', accuracy: 'Good', size: '74M', time: '5-10s' },
    small: { speed: '~6x', accuracy: 'Better', size: '244M', time: '15-30s' },
    medium: { speed: '~2x', accuracy: 'Great', size: '769M', time: '30-60s' },
    large: { speed: '~1x', accuracy: 'Best', size: '1550M', time: '60-120s' }
  };

  const engineInfo = {
    tfidf: { 
      name: 'TF-IDF', 
      description: 'Fast keyword-based statistical matching',
      accuracy: 75,
      speed: 'Instant',
      icon: Gauge,
      color: 'blue'
    },
    neural: { 
      name: 'Neural (BERT)', 
      description: 'Deep learning semantic understanding',
      accuracy: 90,
      speed: 'Fast',
      icon: Sparkles,
      color: 'purple'
    },
    hybrid: { 
      name: 'Hybrid Engine', 
      description: 'Combined TF-IDF + Neural for maximum accuracy',
      accuracy: 95,
      speed: 'Medium',
      icon: Zap,
      color: 'amber'
    }
  };

  const sbertInfo = {
    'all-MiniLM-L6-v2': { speed: 'Fast', quality: 'Good', dims: '384', size: '80MB' },
    'all-mpnet-base-v2': { speed: 'Medium', quality: 'Best', dims: '768', size: '420MB' },
    'paraphrase-MiniLM-L6-v2': { speed: 'Fast', quality: 'Good', dims: '384', size: '80MB' }
  };

  if (!isOpen) return null;

  const tierConfig = tiers[currentTier];
  const isLocked = (value, list) => !list.includes(value);

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-slate-950 border border-slate-800/50 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-2xl shadow-black/50 animate-in slide-in-from-bottom-4 duration-300">
        
        {/* Header */}
        <div className="relative border-b border-slate-800/50 bg-gradient-to-br from-slate-900/50 to-slate-950">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-amber-500/5" />
          <div className="relative px-8 py-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">Processing Configuration</h2>
                <p className="text-sm text-slate-400">Customize AI models and performance settings</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <TierBadge tier={currentTier} size="lg" />
              <button 
                onClick={onClose}
                className="w-10 h-10 flex items-center justify-center rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 text-slate-400 hover:text-white transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="p-8 space-y-6">

            {/* Premium Upgrade Banner */}
            {currentTier === 'free' && (
              <div className="relative group overflow-hidden rounded-2xl border border-amber-500/20 bg-gradient-to-br from-amber-500/10 via-orange-500/10 to-amber-500/5 p-6">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(251,191,36,0.15),transparent_50%)]" />
                <div className="relative flex items-start gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/25 flex-shrink-0">
                    <Crown className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-white mb-2">Unlock Premium Features</h3>
                    <p className="text-slate-300 mb-4 text-sm leading-relaxed">
                      Get access to advanced AI models, GPU acceleration, neural embeddings, and hybrid matching for superior accuracy
                    </p>
                    <button
                      onClick={() => { onChangeTier('premium'); onClose(); }}
                      className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-bold rounded-xl shadow-lg shadow-amber-500/25 hover:shadow-amber-500/40 transition-all"
                    >
                      <Crown className="w-4 h-4" />
                      Upgrade to Premium
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* GPU Status Card (Premium Only) */}
            {currentTier === 'premium' && (
              <div className="relative group overflow-hidden rounded-2xl border border-green-500/20 bg-gradient-to-br from-green-500/10 via-blue-500/10 to-green-500/5">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,197,94,0.15),transparent_50%)]" />
                <div className="relative p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/25">
                        <Zap className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white mb-1">GPU Acceleration</h3>
                        {loadingGPU ? (
                          <div className="flex items-center gap-2">
                            <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
                            <span className="text-sm text-slate-400">Checking GPU status...</span>
                          </div>
                        ) : gpuStatus?.available ? (
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            <span className="text-sm text-green-400 font-medium">{gpuStatus.name} Available</span>
                          </div>
                        ) : (
                          <span className="text-sm text-slate-400">GPU not available</span>
                        )}
                      </div>
                    </div>
                    {gpuStatus?.temperature_c && (
                      <div className={`px-3 py-1.5 rounded-lg text-sm font-bold ${
                        gpuStatus.temp_safe 
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}>
                        🌡️ {gpuStatus.temperature_c}°C
                      </div>
                    )}
                  </div>
                  
                  {gpuStatus?.available && (
                    <>
                      {/* GPU Memory Stats */}
                      <div className="grid grid-cols-3 gap-3 mb-6">
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/50">
                          <div className="text-xs text-slate-400 mb-2">Total Memory</div>
                          <div className="text-2xl font-bold text-white">{gpuStatus.memory_total_gb?.toFixed(1)} GB</div>
                        </div>
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/50">
                          <div className="text-xs text-slate-400 mb-2">Available</div>
                          <div className="text-2xl font-bold text-green-400">{gpuStatus.memory_free_gb?.toFixed(1)} GB</div>
                        </div>
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/50">
                          <div className="text-xs text-slate-400 mb-2">Speedup</div>
                          <div className="text-2xl font-bold text-blue-400">5-10x</div>
                        </div>
                      </div>

                      {/* GPU Toggle */}
                      <label className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl cursor-pointer hover:bg-slate-900/70 transition-all border border-slate-800/50 group">
                        <div className="flex items-center gap-4">
                          <div className={`relative w-14 h-7 rounded-full transition-all ${
                            config.use_gpu 
                              ? 'bg-gradient-to-r from-green-500 to-blue-600' 
                              : 'bg-slate-700'
                          }`}>
                            <div className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-lg transition-transform ${
                              config.use_gpu ? 'translate-x-7' : ''
                            }`} />
                          </div>
                          <div>
                            <div className="font-bold text-white mb-0.5">Enable GPU Acceleration</div>
                            <div className="text-sm text-slate-400">Process 5-10x faster with {gpuStatus.name}</div>
                          </div>
                        </div>
                        <input
                          type="checkbox"
                          checked={config.use_gpu}
                          onChange={(e) => setConfig(prev => ({ ...prev, use_gpu: e.target.checked }))}
                          className="sr-only"
                        />
                        <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${config.use_gpu ? 'rotate-90' : ''}`} />
                      </label>

                      {/* Performance Estimate */}
                      {config.use_gpu && (
                        <div className="mt-4 grid grid-cols-2 gap-3">
                          <div className="bg-green-500/10 rounded-lg p-3 border border-green-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <Rocket className="w-4 h-4 text-green-400" />
                              <div className="text-xs text-green-400">Whisper Speed</div>
                            </div>
                            <div className="text-lg font-bold text-green-400">⚡ 3-5x faster</div>
                          </div>
                          <div className="bg-blue-500/10 rounded-lg p-3 border border-blue-500/20">
                            <div className="flex items-center gap-2 mb-1">
                              <Sparkles className="w-4 h-4 text-blue-400" />
                              <div className="text-xs text-blue-400">Neural Matching</div>
                            </div>
                            <div className="text-lg font-bold text-blue-400">⚡ 5-10x faster</div>
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {!gpuStatus?.available && (
                    <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/50 text-center">
                      <Cpu className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-slate-400 text-sm">🖥️ GPU not available on this server</p>
                      <p className="text-xs text-slate-500 mt-1">Processing will use CPU (still fast!)</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Whisper Model Selection */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center border border-blue-500/20">
                    <Rocket className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Speech Recognition Model</h3>
                    <p className="text-sm text-slate-400">Choose Whisper model for audio transcription</p>
                  </div>
                </div>
                <button
                  onClick={() => setActiveSection(activeSection === 'whisper' ? null : 'whisper')}
                  className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1"
                >
                  <Info className="w-4 h-4" />
                  {activeSection === 'whisper' ? 'Hide' : 'Show'} details
                </button>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                {Object.entries(whisperInfo).map(([model, info]) => {
                  const locked = isLocked(model, tierConfig.whisper);
                  const isSelected = config.whisper_model === model;
                  
                  return (
                    <button
                      key={model}
                      onClick={() => !locked && setConfig(prev => ({ ...prev, whisper_model: model }))}
                      disabled={locked}
                      className={`relative p-4 rounded-xl border-2 text-left transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/25'
                          : locked
                          ? 'border-slate-800/50 bg-slate-900/30 opacity-50 cursor-not-allowed'
                          : 'border-slate-800/50 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-900/70'
                      }`}
                    >
                      {locked && (
                        <div className="absolute top-2 right-2">
                          <Lock className="w-4 h-4 text-amber-500" />
                        </div>
                      )}
                      {isSelected && (
                        <div className="absolute top-2 right-2 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      )}
                      <div className="font-bold text-white text-base mb-3 uppercase">{model}</div>
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">Speed</span>
                          <span className={`font-semibold ${isSelected ? 'text-blue-400' : 'text-slate-300'}`}>
                            {info.speed}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">Quality</span>
                          <span className={`font-semibold ${isSelected ? 'text-blue-400' : 'text-slate-300'}`}>
                            {info.accuracy}
                          </span>
                        </div>
                        {activeSection === 'whisper' && (
                          <>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">Size</span>
                              <span className="font-mono text-slate-500 text-[10px]">{info.size}</span>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">Time</span>
                              <span className="font-mono text-slate-500 text-[10px]">{info.time}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Matching Engine Selection */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center border border-purple-500/20">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Matching Algorithm</h3>
                  <p className="text-sm text-slate-400">Select how to match transcription with songs</p>
                </div>
              </div>

              <div className="space-y-3">
                {Object.entries(engineInfo).map(([engine, info]) => {
                  const locked = isLocked(engine, tierConfig.engines);
                  const isSelected = config.engine === engine;
                  const Icon = info.icon;
                  
                  return (
                    <button
                      key={engine}
                      onClick={() => !locked && setConfig(prev => ({ ...prev, engine }))}
                      disabled={locked}
                      className={`relative w-full p-5 rounded-xl border-2 text-left transition-all ${
                        isSelected
                          ? `border-${info.color}-500 bg-${info.color}-500/10 shadow-lg shadow-${info.color}-500/25`
                          : locked
                          ? 'border-slate-800/50 bg-slate-900/30 opacity-50 cursor-not-allowed'
                          : 'border-slate-800/50 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-900/70'
                      }`}
                    >
                      {locked && (
                        <div className="absolute top-4 right-4 flex items-center gap-2">
                          <span className="text-xs font-bold text-amber-500 uppercase">Premium</span>
                          <Lock className="w-5 h-5 text-amber-500" />
                        </div>
                      )}
                      {isSelected && (
                        <div className={`absolute top-4 right-4 w-6 h-6 bg-${info.color}-500 rounded-full flex items-center justify-center`}>
                          <Check className="w-4 h-4 text-white" />
                        </div>
                      )}
                      
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 bg-${info.color}-500/10 rounded-xl flex items-center justify-center border border-${info.color}-500/20 flex-shrink-0`}>
                          <Icon className={`w-6 h-6 text-${info.color}-400`} />
                        </div>
                        <div className="flex-1">
                          <div className="font-bold text-white text-xl mb-2">{info.name}</div>
                          <div className="text-slate-300 text-sm mb-4">{info.description}</div>
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                              <div className="text-xs text-slate-400">Accuracy</div>
                              <div className="flex items-center gap-1">
                                {[...Array(5)].map((_, i) => (
                                  <div
                                    key={i}
                                    className={`w-1.5 h-4 rounded-full ${
                                      i < Math.round(info.accuracy / 20) ? `bg-${info.color}-500` : 'bg-slate-700'
                                    }`}
                                  />
                                ))}
                              </div>
                              <div className={`text-sm font-bold text-${info.color}-400`}>{info.accuracy}%</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-slate-400" />
                              <div className="text-sm text-slate-400">{info.speed}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* SBERT Model Selection */}
            {(config.engine === 'neural' || config.engine === 'hybrid') && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-amber-500/10 rounded-lg flex items-center justify-center border border-amber-500/20">
                    <Crown className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Neural Model (BERT)</h3>
                    <p className="text-sm text-slate-400">Advanced semantic embedding model</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {Object.entries(sbertInfo).map(([model, info]) => {
                    const locked = isLocked(model, tierConfig.sbert);
                    const isSelected = config.sbert_model === model;
                    
                    return (
                      <button
                        key={model}
                        onClick={() => !locked && setConfig(prev => ({ ...prev, sbert_model: model }))}
                        disabled={locked}
                        className={`relative w-full p-4 rounded-xl border-2 text-left transition-all ${
                          isSelected
                            ? 'border-purple-500 bg-purple-500/10 shadow-lg shadow-purple-500/25'
                            : locked
                            ? 'border-slate-800/50 bg-slate-900/30 opacity-50 cursor-not-allowed'
                            : 'border-slate-800/50 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-900/70'
                        }`}
                      >
                        {locked && (
                          <div className="absolute top-3 right-3">
                            <Lock className="w-5 h-5 text-amber-500" />
                          </div>
                        )}
                        {isSelected && (
                          <div className="absolute top-3 right-3 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                            <Check className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div className="font-mono text-white font-semibold mb-3 pr-8">{model}</div>
                        <div className="grid grid-cols-4 gap-3 text-sm">
                          <div>
                            <div className="text-xs text-slate-400 mb-1">Speed</div>
                            <div className={`font-semibold ${isSelected ? 'text-purple-400' : 'text-slate-300'}`}>{info.speed}</div>
                          </div>
                          <div>
                            <div className="text-xs text-slate-400 mb-1">Quality</div>
                            <div className={`font-semibold ${isSelected ? 'text-purple-400' : 'text-slate-300'}`}>{info.quality}</div>
                          </div>
                          <div>
                            <div className="text-xs text-slate-400 mb-1">Dimensions</div>
                            <div className="font-mono text-xs text-slate-500">{info.dims}</div>
                          </div>
                          <div>
                            <div className="text-xs text-slate-400 mb-1">Size</div>
                            <div className="font-mono text-xs text-slate-500">{info.size}</div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Configuration Summary */}
            <div className="relative overflow-hidden rounded-2xl border border-slate-800/50 bg-slate-900/50 p-6">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-transparent" />
              <div className="relative">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Configuration Summary
                </h3>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-2">Tier</div>
                    <div className="font-bold text-white">{currentTier.toUpperCase()}</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-2">Whisper Model</div>
                    <div className="font-bold text-white">{config.whisper_model.toUpperCase()}</div>
                  </div>
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                    <div className="text-xs text-slate-400 mb-2">Engine</div>
                    <div className="font-bold text-white">{config.engine.toUpperCase()}</div>
                  </div>
                  <div className={`rounded-xl p-4 border ${
                    config.use_gpu 
                      ? 'bg-green-500/10 border-green-500/30' 
                      : 'bg-slate-800/50 border-slate-700/50'
                  }`}>
                    <div className="text-xs text-slate-400 mb-2">Processing</div>
                    <div className={`font-bold flex items-center gap-2 ${
                      config.use_gpu ? 'text-green-400' : 'text-white'
                    }`}>
                      {config.use_gpu ? (
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

                {/* Estimated Processing Time */}
                <div className="mt-4 pt-4 border-t border-slate-800/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-slate-400" />
                      <span className="text-sm text-slate-400">Estimated processing time:</span>
                    </div>
                    <div className="text-lg font-bold text-white">
                      {whisperInfo[config.whisper_model].time}
                      {config.use_gpu && <span className="text-sm text-green-400 ml-2">(with GPU boost)</span>}
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Footer with CTA */}
        <div className="relative border-t border-slate-800/50 bg-slate-900/50 p-6">
          <div className="absolute inset-0 bg-gradient-to-t from-blue-500/5 to-transparent" />
          <div className="relative flex items-center justify-between gap-4">
            <div className="flex-1">
              <div className="text-sm text-slate-400 mb-1">Ready to process with optimized settings</div>
              <div className="text-xs text-slate-500">
                {config.engine === 'hybrid' && 'Using hybrid engine for maximum accuracy'}
                {config.engine === 'neural' && 'Using neural matching for semantic understanding'}
                {config.engine === 'tfidf' && 'Using fast keyword-based matching'}
              </div>
            </div>
            <button
              onClick={() => onStart(config)}
              className="group relative px-8 py-4 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 bg-size-200 hover:bg-pos-100 text-white font-bold rounded-xl shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all text-lg flex items-center gap-3"
            >
              <span>Start Processing</span>
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-white/0 via-white/20 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity" 
                   style={{ transform: 'translateX(-100%)', animation: 'shimmer 2s infinite' }} />
            </button>
          </div>
        </div>

      </div>

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .bg-size-200 { background-size: 200% 100%; }
        .bg-pos-100 { background-position: 100% 0; }
      `}</style>
    </div>
  );
};