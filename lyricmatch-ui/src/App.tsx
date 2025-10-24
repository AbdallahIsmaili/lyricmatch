import React, { useState, useEffect, useRef } from 'react';
import { Music, Upload, Loader2, Trophy, Medal, RefreshCw, Sparkles, Zap, Shield, Sun, Moon, History, Info, Activity, Crown, Rocket, Check, Lock, Star, Settings, ChevronDown, X, Plus } from 'lucide-react';

// Add after imports, before other code
const DB_NAME = 'LyricMatchDB';
const STORE_NAME = 'searchHistory';

const initDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
        store.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
};

const saveToHistory = async (data) => {
  try {
    const db = await initDB();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    
    const historyItem = {
      ...data,
      timestamp: new Date().toISOString()
    };
    
    await store.add(historyItem);
  } catch (error) {
    console.error('Error saving to history:', error);
  }
};

const getHistory = async (limit = 20) => {
  try {
    const db = await initDB();
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const index = store.index('timestamp');
    
    return new Promise((resolve, reject) => {
      const request = index.openCursor(null, 'prev');
      const results = [];
      
      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor && results.length < limit) {
          results.push(cursor.value);
          cursor.continue();
        } else {
          resolve(results);
        }
      };
      
      request.onerror = () => reject(request.error);
    });
  } catch (error) {
    console.error('Error getting history:', error);
    return [];
  }
};

const clearHistory = async () => {
  try {
    const db = await initDB();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    await store.clear();
  } catch (error) {
    console.error('Error clearing history:', error);
  }
};

const themeStyles = `
  :root[data-theme="dark"] {
    --bg-primary: #000000;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #262626;
    --bg-header: rgba(0, 0, 0, 0.95);
    --text-primary: #ffffff;
    --text-secondary: #9ca3af;
    --text-tertiary: #6b7280;
    --border: #333333;
    --accent: #ffffff;
    --accent-secondary: #9ca3af;
    --premium: #fbbf24;
    --premium-glow: rgba(251, 191, 36, 0.3);
  }

  :root[data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f3f4f6;
    --bg-tertiary: #e5e7eb;
    --bg-header: rgba(255, 255, 255, 0.95);
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --text-tertiary: #9ca3af;
    --border: #d1d5db;
    --accent: #111827;
    --accent-secondary: #4b5563;
    --premium: #f59e0b;
    --premium-glow: rgba(245, 158, 11, 0.3);
  }

  * {
    transition-property: background-color, border-color, color;
    transition-duration: 300ms;
    transition-timing-function: ease-in-out;
  }

  @keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
  }

  .premium-shimmer {
    background: linear-gradient(90deg, transparent, var(--premium-glow), transparent);
    background-size: 200% 100%;
    animation: shimmer 3s infinite;
  }
`;

if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = themeStyles;
  document.head.appendChild(styleElement);
}

// Theme Context
const ThemeContext = React.createContext();
const useTheme = () => React.useContext(ThemeContext);

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return document.documentElement.getAttribute('data-theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Tier Badge Component
const TierBadge = ({ tier, size = 'sm' }) => {
  const isPremium = tier === 'premium';
  const sizeClasses = size === 'lg' ? 'px-4 py-2 text-base' : 'px-3 py-1 text-xs';
  
  return (
    <div className={`inline-flex items-center gap-1.5 ${sizeClasses} rounded-full font-bold uppercase tracking-wider ${
      isPremium 
        ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black shadow-lg shadow-yellow-500/50' 
        : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] border border-[var(--border)]'
    }`}>
      {isPremium ? <Crown className={size === 'lg' ? 'w-5 h-5' : 'w-3 h-3'} /> : <Zap className={size === 'lg' ? 'w-5 h-5' : 'w-3 h-3'} />}
      <span>{tier === 'premium' ? 'Premium' : 'Free'}</span>
    </div>
  );
};

// Configuration Modal
const ConfigModal = ({ isOpen, onClose, onStart, currentTier, onChangeTier }) => {
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

          {/* SBERT Model Selection (Neural/Hybrid only) */}
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

// Tier Selection Modal
const TierSelectionModal = ({ isOpen, onClose, onSelectTier }) => {
  if (!isOpen) return null;

  const tiers = [
    {
      id: 'free',
      name: 'Free',
      icon: Zap,
      price: '$0',
      period: 'forever',
      features: [
        'Basic TF-IDF matching',
        'Tiny & Base Whisper models',
        'Fast processing',
        'Up to 5 searches per day',
        '10MB max file size'
      ],
      limitations: [
        'No neural embeddings',
        'No hybrid matching',
        'Limited models'
      ]
    },
    {
      id: 'premium',
      name: 'Premium',
      icon: Crown,
      price: 'FREE',
      period: 'beta access',
      features: [
        'Advanced Neural Embeddings (BERT)',
        'Hybrid matching algorithms',
        'All Whisper models (tiny → large)',
        'Unlimited searches',
        '50MB max file size',
        'Priority processing',
        'Higher accuracy results',
        'Multiple SBERT models'
      ],
      limitations: [],
      popular: true
    }
  ];

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-[var(--border)] text-center bg-gradient-to-r from-[var(--bg-secondary)] to-transparent">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Choose Your Plan</h2>
          <p className="text-[var(--text-secondary)] text-lg">Select the tier that fits your needs</p>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-200px)] p-8">
          <div className="grid md:grid-cols-2 gap-6">
            {tiers.map((tier) => {
              const Icon = tier.icon;
              const isPremium = tier.id === 'premium';
              
              return (
                <div
                  key={tier.id}
                  className={`relative rounded-2xl border-2 p-8 transition-all ${
                    isPremium
                      ? 'border-yellow-500 bg-gradient-to-br from-yellow-500/10 to-orange-500/5 shadow-xl shadow-yellow-500/20'
                      : 'border-[var(--border)] bg-[var(--bg-secondary)]'
                  }`}
                >
                  {tier.popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <div className="px-4 py-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-bold text-sm rounded-full shadow-lg">
                        RECOMMENDED
                      </div>
                    </div>
                  )}

                  <div className="text-center mb-6">
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 ${
                      isPremium
                        ? 'bg-gradient-to-br from-yellow-500 to-orange-500'
                        : 'bg-[var(--bg-tertiary)]'
                    }`}>
                      <Icon className={`w-8 h-8 ${isPremium ? 'text-black' : 'text-[var(--text-primary)]'}`} />
                    </div>
                    <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-2">{tier.name}</h3>
                    <div className="flex items-baseline justify-center gap-1">
                      <span className={`text-4xl font-bold ${isPremium ? 'text-yellow-500' : 'text-[var(--text-primary)]'}`}>
                        {tier.price}
                      </span>
                      <span className="text-[var(--text-secondary)]">/ {tier.period}</span>
                    </div>
                  </div>

                  <div className="space-y-3 mb-6">
                    {tier.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 ${isPremium ? 'text-yellow-500' : 'text-green-500'}`} />
                        <span className="text-[var(--text-primary)]">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {tier.limitations.length > 0 && (
                    <div className="space-y-2 mb-6 pt-6 border-t border-[var(--border)]">
                      <p className="text-[var(--text-tertiary)] text-sm font-semibold uppercase">Limitations:</p>
                      {tier.limitations.map((limitation, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <span className="text-[var(--text-tertiary)] text-sm">• {limitation}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={() => {
                      onSelectTier(tier.id);
                      onClose();
                    }}
                    className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
                      isPremium
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black shadow-lg hover:shadow-yellow-500/50'
                        : 'bg-[var(--bg-tertiary)] text-[var(--text-primary)] hover:bg-[var(--accent)] hover:text-[var(--bg-primary)]'
                    }`}
                  >
                    {isPremium ? 'Get Premium Access' : 'Start Free'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        <div className="p-6 border-t border-[var(--border)] bg-[var(--bg-secondary)] text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// Waveform Visualizer Component
const WaveformVisualizer = ({ isActive }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const barsRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const barCount = 50;
    const barWidth = width / barCount;

    if (barsRef.current.length === 0) {
      barsRef.current = Array.from({ length: barCount }, () => ({
        height: Math.random() * 0.5 + 0.2,
        speed: Math.random() * 0.02 + 0.01,
        phase: Math.random() * Math.PI * 2
      }));
    }

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      barsRef.current.forEach((bar, i) => {
        if (isActive) {
          bar.phase += bar.speed;
          bar.height = Math.abs(Math.sin(bar.phase)) * 0.6 + 0.3;
        } else {
          bar.height *= 0.95;
        }

        const barHeight = bar.height * height;
        const x = i * barWidth;
        const y = (height - barHeight) / 2;

        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(156, 163, 175, 0.4)');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth - 2, barHeight);
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={120}
      className="w-full h-32 rounded-xl"
    />
  );
};


const HistoryModal = ({ isOpen, onClose, onSelectItem }) => {
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
      console.log('Loaded history items:', items.length); // Debug
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
              {history.map((item, index) => (
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

const ArtistFetchModal = ({ isOpen, onClose, onFetch }) => {
  const [artistName, setArtistName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  const handleFetch = async () => {
    if (!artistName.trim()) return;
    
    setLoading(true);
    setStatus('Fetching songs...');
    
    try {
      const response = await fetch('http://localhost:5000/api/lyrics/fetch-artist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artist_name: artistName })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus(`✅ Added ${data.songs_added} songs for ${data.artist}`);
        setTimeout(() => {
          onFetch();
          onClose();
        }, 2000);
      } else {
        setStatus(`❌ Error: ${data.error}`);
      }
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


const Header = ({ currentTier, onChangeTier, setShowArtistFetch }) => {
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
              <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">LyricMatch</h1>
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
              {theme === 'dark' ? <Plus className="w-5 h-5 text-[var(--text-primary)]" /> : <Plus className="w-5 h-5 text-[var(--text-primary)]" />}

              <span className="text-sm text-[var(--text-primary)]">Add Artist</span>
            </button>
          </div>
        </div>
      </header>
      <HistoryModal 
        isOpen={showHistory} 
        onClose={() => setShowHistory(false)}
        onSelectItem={(item) => {
          // Could re-display results if needed
          console.log('Selected history item:', item);
        }}
      />
    </>
  );
};


const UploadView = ({ onUpload, currentTier, onOpenConfig }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'record'

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.includes('audio')) {
      onUpload(file);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-full mb-6">
            <Sparkles className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="text-sm font-medium text-[var(--text-secondary)]">AI-Powered Recognition</span>
            <TierBadge tier={currentTier} />
          </div>
          <h2 className="text-5xl font-bold text-[var(--text-primary)] mb-4 tracking-tight">
            Identify Your Song
          </h2>
          <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-6">
            Upload an audio file or record directly to discover the song through advanced lyrics recognition
          </p>
          <button
            onClick={onOpenConfig}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border)] transition-colors text-[var(--text-primary)] font-semibold"
          >
            <Settings className="w-5 h-5" />
            Configure Settings
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-[var(--bg-secondary)] p-2 rounded-xl border border-[var(--border)]">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'upload'
                ? 'bg-[var(--accent)] text-[var(--bg-primary)] shadow-lg'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
            }`}
          >
            <Upload className="w-5 h-5" />
            Upload File
          </button>
          <button
            onClick={() => setActiveTab('record')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'record'
                ? 'bg-[var(--accent)] text-[var(--bg-primary)] shadow-lg'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
            }`}
          >
            <Activity className="w-5 h-5" />
            Record Audio
          </button>
        </div>

        {/* Content */}
        {activeTab === 'upload' ? (
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-16 transition-all duration-300 ${
              isDragging 
                ? 'border-[var(--accent)] bg-[var(--accent)]/10 scale-[1.02]' 
                : 'border-[var(--border)] bg-[var(--bg-secondary)]/50 hover:bg-[var(--bg-secondary)] hover:border-[var(--accent)]/50'
            }`}
          >
            <div className="flex flex-col items-center gap-6">
              <div className="relative">
                <div className="w-28 h-28 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center border border-[var(--border)] shadow-2xl">
                  <Upload className="w-14 h-14 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <Sparkles className="w-3 h-3 text-black" />
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-2xl font-semibold text-[var(--text-primary)] mb-2">Drop your audio file here</p>
                <p className="text-[var(--text-secondary)] text-lg mb-1">or click to browse</p>
                <p className="text-sm text-[var(--text-tertiary)] mt-4 font-mono">
                  MP3 • WAV • M4A • FLAC • OGG • WEBM
                </p>
              </div>

              <input
                type="file"
                accept="audio/*"
                onChange={handleFileInput}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            </div>
          </div>
        ) : (
          <AudioRecorder onRecordingComplete={onUpload} currentTier={currentTier} />
        )}

        <div className="mt-12 grid grid-cols-3 gap-6">
          <div className="group bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-all">
            <Zap className="w-8 h-8 text-[var(--text-primary)] mb-3" />
            <div className="text-2xl font-bold text-[var(--text-primary)] mb-1">Fast</div>
            <div className="text-sm text-[var(--text-secondary)]">Lightning Speed</div>
          </div>
          <div className="group bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-all">
            <Sparkles className="w-8 h-8 text-[var(--text-primary)] mb-3" />
            <div className="text-2xl font-bold text-[var(--text-primary)] mb-1">Accurate</div>
            <div className="text-sm text-[var(--text-secondary)]">AI-Powered</div>
          </div>
          <div className="group bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-all">
            <Shield className="w-8 h-8 text-[var(--text-primary)] mb-3" />
            <div className="text-2xl font-bold text-[var(--text-primary)] mb-1">Secure</div>
            <div className="text-sm text-[var(--text-secondary)]">Private</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AudioRecorder = ({ onRecordingComplete, currentTier }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const animationRef = useRef(null);

  const maxDuration = currentTier === 'premium' ? 120 : 30; // seconds

  useEffect(() => {
    return () => {
      stopRecording();
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      // Setup audio analysis
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      // Start visualization
      visualizeAudio();

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
        onRecordingComplete(file);
        
        // Cleanup
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setDuration(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          const newDuration = prev + 1;
          if (newDuration >= maxDuration) {
            stopRecording();
            return maxDuration;
          }
          return newDuration;
        });
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please grant permission and try again.');
    }
  };

  const visualizeAudio = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const animate = () => {
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(average / 255);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        timerRef.current = setInterval(() => {
          setDuration(prev => {
            const newDuration = prev + 1;
            if (newDuration >= maxDuration) {
              stopRecording();
              return maxDuration;
            }
            return newDuration;
          });
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        clearInterval(timerRef.current);
      }
      setIsPaused(!isPaused);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-8 border border-[var(--border)]">
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-full mb-4">
          <Activity className="w-4 h-4 text-red-500" />
          <span className="text-sm font-semibold text-red-500">
            {isRecording ? (isPaused ? 'Recording Paused' : 'Recording...') : 'Ready to Record'}
          </span>
        </div>
        <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
          Record Audio
        </h3>
        <p className="text-[var(--text-secondary)]">
          Max duration: {maxDuration}s {currentTier === 'free' && '(Upgrade for 120s)'}
        </p>
      </div>

      {/* Waveform Visualization */}
      {isRecording && (
        <div className="mb-6 h-32 bg-[var(--bg-tertiary)] rounded-xl flex items-center justify-center overflow-hidden relative">
          <div className="absolute inset-0 flex items-center justify-center gap-1">
            {[...Array(50)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-red-500 to-orange-500 rounded-full transition-all duration-100"
                style={{
                  height: `${Math.random() * audioLevel * 100 + 20}%`,
                  opacity: isPaused ? 0.3 : 1
                }}
              />
            ))}
          </div>
          {isPaused && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
              <div className="text-white text-xl font-bold">PAUSED</div>
            </div>
          )}
        </div>
      )}

      {/* Timer Display */}
      <div className="mb-6 text-center">
        <div className="text-5xl font-mono font-bold text-[var(--text-primary)] mb-2">
          {formatTime(duration)}
        </div>
        <div className="h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-300"
            style={{ width: `${(duration / maxDuration) * 100}%` }}
          />
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-bold rounded-xl shadow-lg transition-all"
          >
            <div className="w-6 h-6 rounded-full bg-white" />
            Start Recording
          </button>
        ) : (
          <>
            <button
              onClick={pauseRecording}
              className="flex items-center gap-2 px-6 py-4 bg-[var(--bg-tertiary)] hover:bg-[var(--accent)]/10 text-[var(--text-primary)] font-semibold rounded-xl transition-all"
            >
              {isPaused ? (
                <>
                  <div className="w-0 h-0 border-l-8 border-l-[var(--text-primary)] border-y-6 border-y-transparent" />
                  Resume
                </>
              ) : (
                <>
                  <div className="flex gap-1">
                    <div className="w-2 h-6 bg-[var(--text-primary)] rounded" />
                    <div className="w-2 h-6 bg-[var(--text-primary)] rounded" />
                  </div>
                  Pause
                </>
              )}
            </button>
            <button
              onClick={stopRecording}
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-xl shadow-lg transition-all"
            >
              <div className="w-6 h-6 bg-white rounded" />
              Stop & Analyze
            </button>
          </>
        )}
      </div>

      {currentTier === 'free' && (
        <div className="mt-6 text-center text-sm text-[var(--text-secondary)]">
          <Crown className="w-4 h-4 inline mr-1 text-yellow-500" />
          Upgrade to Premium for 120s recordings
        </div>
      )}
    </div>
  );
};

// Processing View Component
const ProcessingView = ({ progress, filename, status, tier, config }) => {
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

// Results View Component

const ResultsView = ({ results, onReset, tier, config }) => {
  const [spotifyData, setSpotifyData] = useState(null);
  const [youtubeData, setYoutubeData] = useState(null);
  const [loading, setLoading] = useState(true);

  if (!results || !results.topMatch) {
    return (
      <div className="text-center text-[var(--text-primary)]">
        <p>No results to display</p>
        <button onClick={onReset} className="mt-4 px-6 py-3 bg-[var(--accent)] text-white rounded-lg font-semibold">
          Try Again
        </button>
      </div>
    );
  }

  const { topMatch, transcription, audioInfo } = results;

  useEffect(() => {
    fetchMusicData();
  }, [topMatch]);

  const fetchMusicData = async () => {
    setLoading(true);
    try {
      // Fetch Spotify and YouTube data
      const [spotifyResponse, youtubeResponse] = await Promise.all([
        fetchSpotifyTrack(topMatch.artist, topMatch.title),
        fetchYouTubeVideo(topMatch.artist, topMatch.title)
      ]);
      
      console.log('Spotify response:', spotifyResponse); // Debug
      setSpotifyData(spotifyResponse);
      setYoutubeData(youtubeResponse);
    } catch (error) {
      console.error('Error fetching music data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-4 shadow-2xl animate-pulse">
          <Trophy className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-4xl md:text-5xl font-bold text-[var(--text-primary)] mb-3">
          Perfect Match Found!
        </h2>
        <div className="flex items-center justify-center gap-3 mt-4">
          <TierBadge tier={tier} size="lg" />
          <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-full">
            <span className="text-green-500 font-bold text-lg">{Math.round(topMatch.final_score * 100)}% Match</span>
          </div>
        </div>
      </div>

      {/* Main Track Card */}
      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 rounded-3xl blur-3xl animate-pulse" />
        <div className="relative bg-[var(--bg-secondary)] rounded-3xl overflow-hidden border border-[var(--border)] shadow-2xl">
          <div className="grid md:grid-cols-2 gap-0">
            {/* Album Art Section */}
            <div className="relative h-96 bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900 flex items-center justify-center overflow-hidden">
              {loading ? (
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-16 h-16 text-white animate-spin" />
                  <p className="text-white/60">Loading track info...</p>
                </div>
              ) : spotifyData?.image ? (
                <img 
                  src={spotifyData.image} 
                  alt={topMatch.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <>
                  <div className="absolute inset-0 opacity-20">
                    <div className="absolute inset-0" style={{
                      backgroundImage: 'radial-gradient(circle at 30% 50%, rgba(255,255,255,0.15) 0%, transparent 50%)',
                    }} />
                  </div>
                  <Music className="w-32 h-32 text-white/80 relative z-10" />
                </>
              )}
              <div className="absolute bottom-4 right-4 px-4 py-2 bg-black/80 backdrop-blur-sm rounded-full border border-white/20">
                <span className="text-green-400 text-xl font-bold">{Math.round(topMatch.final_score * 100)}%</span>
              </div>
            </div>

            {/* Track Info Section */}
            <div className="p-8 flex flex-col justify-between">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full mb-4">
                  <Crown className="w-4 h-4 text-yellow-500" />
                  <span className="text-yellow-500 text-sm font-bold uppercase">Best Match</span>
                </div>
                
                <h3 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-3 leading-tight">
                  {topMatch.title}
                </h3>
                <p className="text-2xl text-[var(--text-secondary)] mb-6">{topMatch.artist}</p>
                
                <div className="flex flex-wrap gap-3 mb-6">
                  {topMatch.album && (
                    <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
                      <span className="text-xs text-[var(--text-tertiary)]">Album:</span>
                      <span className="ml-2 text-[var(--text-primary)] font-semibold">{topMatch.album}</span>
                    </div>
                  )}
                  {topMatch.year && (
                    <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
                      <span className="text-xs text-[var(--text-tertiary)]">Year:</span>
                      <span className="ml-2 text-[var(--text-primary)] font-semibold">{topMatch.year}</span>
                    </div>
                  )}
                </div>

                {/* Match Quality Bar */}
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-[var(--text-tertiary)]">Confidence Score</span>
                    <span className="text-lg font-bold text-green-500">Excellent Match</span>
                  </div>
                  <div className="h-3 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-1000"
                      style={{ width: `${topMatch.final_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Streaming Buttons */}
              <div className="space-y-3">
                <StreamingButton
                  platform="spotify"
                  url={spotifyData?.url}
                  loading={loading}
                  artist={topMatch.artist}
                  title={topMatch.title}
                  previewUrl={spotifyData?.preview_url}
                />
                <StreamingButton
                  platform="youtube"
                  url={youtubeData?.url}
                  loading={loading}
                  artist={topMatch.artist}
                  title={topMatch.title}
                  previewUrl={null}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Match Explanation */}
      <MatchExplanation match={topMatch} tier={tier} engine={config?.engine} />

      {/* Lyrics Match */}
      {transcription && topMatch.lyrics_cleaned && (
        <LyricsMatchDisplay
          queryText={transcription}
          songLyrics={topMatch.lyrics_cleaned}
          matchPercentage={topMatch.match_percentage || 0}
        />
      )}

      {/* Audio Info */}
      {audioInfo && (
        <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
          <h3 className="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Audio Analysis
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Sample Rate</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.sample_rate ? `${(audioInfo.sample_rate / 1000).toFixed(1)} kHz` : 'N/A'}
              </p>
            </div>
            
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Duration</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.duration ? `${audioInfo.duration.toFixed(1)}s` : 'N/A'}
              </p>
            </div>
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Engine</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {config?.engine?.toUpperCase() || 'TF-IDF'}
              </p>
            </div>
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Accuracy</p>
              <p className="text-xl font-bold text-green-500">
                {Math.round(topMatch.final_score * 100)}%
              </p>
            </div>

            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Bitrate</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.bitrate ? `${audioInfo.bitrate} kbps` : 'N/A'}
              </p>
            </div>
            
            {/* NEW */}
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">Channels</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.channels === 2 ? 'Stereo' : 'Mono'}
              </p>
            </div>
            
            {/* NEW */}
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-tertiary)] mb-1">File Size</p>
              <p className="text-xl font-bold text-[var(--text-primary)]">
                {audioInfo.file_size_mb ? `${audioInfo.file_size_mb} MB` : 'N/A'}
              </p>
            </div>

          </div>
        </div>
      )}

      {/* Try Again */}
      <div className="text-center pt-8">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] hover:opacity-90 text-[var(--bg-primary)] font-bold rounded-2xl shadow-2xl transition-all transform hover:scale-105 text-lg"
        >
          <RefreshCw className="w-6 h-6" />
          Analyze Another Song
        </button>
      </div>
    </div>
  );
};


const StreamingButton = ({ platform, url, loading, artist, title, previewUrl }) => {
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


// Fetch Spotify Track - Add this helper function
const fetchSpotifyTrack = async (artist, title) => {
  try {
    const response = await fetch(`http://localhost:5000/api/spotify/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Spotify data:', data);
      return data; 
    }
  } catch (error) {
    console.error('Spotify fetch error:', error);
  }
  return null;
};

// Fetch YouTube Video - Add this helper function
const fetchYouTubeVideo = async (artist, title) => {
  try {
    // This would call your backend API endpoint that handles YouTube API
    const response = await fetch(`http://localhost:5000/api/youtube/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('YouTube fetch error:', error);
  }
  return null;
};



const LyricsMatchDisplay = ({ queryText, songLyrics, matchPercentage }) => {
  const [highlightedLyrics, setHighlightedLyrics] = useState([]);
  const [matchingSegments, setMatchingSegments] = useState([]);

  useEffect(() => {
    if (queryText && songLyrics) {
      findAndHighlightMatches();
    }
  }, [queryText, songLyrics]);

  const findAndHighlightMatches = () => {
    const queryWords = queryText.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    const lyricWords = songLyrics.toLowerCase().split(/\s+/);
    const originalWords = songLyrics.split(/\s+/);
    
    // Create a map of which words match
    const matchMap = lyricWords.map((word, idx) => {
      const cleanWord = word.replace(/[^\w]/g, '');
      return queryWords.some(qw => {
        const cleanQw = qw.replace(/[^\w]/g, '');
        return cleanWord === cleanQw || 
               cleanWord.includes(cleanQw) || 
               cleanQw.includes(cleanWord);
      });
    });

    // Find consecutive matching segments
    const segments = [];
    let currentSegment = null;
    
    for (let i = 0; i < matchMap.length; i++) {
      if (matchMap[i]) {
        if (!currentSegment) {
          currentSegment = { start: i, end: i, words: [originalWords[i]] };
        } else {
          currentSegment.end = i;
          currentSegment.words.push(originalWords[i]);
        }
      } else {
        if (currentSegment && currentSegment.words.length >= 2) {
          segments.push({
            ...currentSegment,
            text: currentSegment.words.join(' ')
          });
        }
        currentSegment = null;
      }
    }
    
    // Add last segment if exists
    if (currentSegment && currentSegment.words.length >= 2) {
      segments.push({
        ...currentSegment,
        text: currentSegment.words.join(' ')
      });
    }

    // Create highlighted lyrics display
    const highlighted = [];
    let lastIdx = 0;
    
    segments.forEach(segment => {
      // Add non-matching text before segment
      if (segment.start > lastIdx) {
        highlighted.push({
          text: originalWords.slice(lastIdx, segment.start).join(' '),
          isMatch: false
        });
      }
      
      // Add matching segment
      highlighted.push({
        text: segment.text,
        isMatch: true
      });
      
      lastIdx = segment.end + 1;
    });
    
    // Add remaining text
    if (lastIdx < originalWords.length) {
      highlighted.push({
        text: originalWords.slice(lastIdx).join(' '),
        isMatch: false
      });
    }

    setHighlightedLyrics(highlighted);
    setMatchingSegments(segments.slice(0, 5)); // Top 5 segments
  };

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Lyrics Analysis
        </h3>
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold text-green-500">
            {matchPercentage.toFixed(1)}%
          </div>
          <span className="text-sm text-[var(--text-secondary)]">match</span>
        </div>
      </div>
      
      {/* Match Progress Bar */}
      <div className="mb-6">
        <div className="h-3 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-green-500 via-blue-500 to-purple-500 rounded-full transition-all duration-1000"
            style={{ width: `${matchPercentage}%` }}
          />
        </div>
      </div>

      {/* Top Matching Segments */}
      {matchingSegments.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase">
            Top Matching Phrases
          </h4>
          <div className="space-y-2">
            {matchingSegments.map((segment, idx) => (
              <div 
                key={idx}
                className="group bg-gradient-to-r from-green-500/10 to-blue-500/10 hover:from-green-500/20 hover:to-blue-500/20 border border-green-500/30 rounded-lg p-3 transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center text-white font-bold text-xs">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-[var(--text-primary)] font-medium leading-relaxed">
                      "{segment.text}"
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-1">
                      {segment.words.length} words matched
                    </p>
                  </div>
                  <Check className="w-5 h-5 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Lyrics with Highlighting */}
      <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 max-h-96 overflow-y-auto">
        <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase sticky top-0 bg-[var(--bg-tertiary)] pb-2">
          Song Lyrics (Matches Highlighted)
        </h4>
        <div className="text-[var(--text-primary)] leading-relaxed space-y-2">
          {highlightedLyrics.map((segment, idx) => (
            <span
              key={idx}
              className={segment.isMatch ? 
                'bg-gradient-to-r from-yellow-500/30 to-green-500/30 px-1 py-0.5 rounded font-semibold text-[var(--text-primary)] shadow-sm' : 
                'text-[var(--text-secondary)]'
              }
            >
              {segment.text}{' '}
            </span>
          ))}
        </div>
      </div>

      {matchingSegments.length === 0 && (
        <div className="text-center py-8 text-[var(--text-secondary)]">
          <Info className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No exact phrase matches found</p>
          <p className="text-sm mt-1">Match based on semantic similarity</p>
        </div>
      )}
    </div>
  );
};


const MatchExplanation = ({ match, tier, engine }) => {
  const getExplanation = () => {
    const score = match.final_score * 100;
    const explanations = [];

    if (engine === 'tfidf') {
      explanations.push({
        icon: '📊',
        title: 'TF-IDF Keyword Matching',
        description: 'Analyzed word frequency and importance in the lyrics'
      });
      
      if (score > 70) {
        explanations.push({
          icon: '✅',
          title: 'Strong Keyword Overlap',
          description: `Found ${match.common_word_count || 'many'} matching keywords`
        });
      }
    } else if (engine === 'neural' || engine === 'hybrid') {
      explanations.push({
        icon: '🧠',
        title: 'Neural Semantic Analysis',
        description: 'Used AI to understand meaning and context, not just keywords'
      });
      
      if (match.neural_score && match.neural_score > 0.6) {
        explanations.push({
          icon: '🎯',
          title: 'High Semantic Similarity',
          description: 'The AI detected strong contextual meaning similarity'
        });
      }
      
      if (engine === 'hybrid' && match.fuzzy_score) {
        explanations.push({
          icon: '🔀',
          title: 'Fuzzy Matching Applied',
          description: 'Additional string matching for higher accuracy'
        });
      }
    }

    if (match.match_percentage && match.match_percentage > 50) {
      explanations.push({
        icon: '💯',
        title: `${match.match_percentage.toFixed(0)}% Word Match`,
        description: 'High percentage of words from your audio found in this song'
      });
    }

    if (score > 80) {
      explanations.push({
        icon: '⭐',
        title: 'Excellent Confidence',
        description: 'Very high likelihood this is the correct song'
      });
    } else if (score > 60) {
      explanations.push({
        icon: '👍',
        title: 'Good Confidence',
        description: 'Strong match, likely the correct song'
      });
    } else if (score > 40) {
      explanations.push({
        icon: '🤔',
        title: 'Moderate Confidence',
        description: 'Possible match, but verify with alternatives'
      });
    }

    return explanations;
  };

  const explanations = getExplanation();

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
        <Info className="w-5 h-5" />
        Why This Match?
      </h3>
      
      <div className="space-y-4">
        {explanations.map((exp, idx) => (
          <div key={idx} className="flex items-start gap-4">
            <div className="text-3xl">{exp.icon}</div>
            <div className="flex-1">
              <h4 className="font-semibold text-[var(--text-primary)] mb-1">
                {exp.title}
              </h4>
              <p className="text-[var(--text-secondary)] text-sm">
                {exp.description}
              </p>
            </div>
          </div>
        ))}
        
        <div className="mt-6 pt-4 border-t border-[var(--border)]">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[var(--text-tertiary)]">Match Type:</span>
            <span className="font-mono font-bold text-[var(--text-primary)]">
              {match.match_type?.toUpperCase()}
            </span>
          </div>
          {tier === 'premium' && (
            <div className="mt-2 flex items-center gap-2">
              <Crown className="w-4 h-4 text-yellow-500" />
              <span className="text-xs text-yellow-500 font-semibold">
                Enhanced with Premium AI models
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SongPreview = ({ artist, title, album }) => {
  const searchQuery = encodeURIComponent(`${artist} ${title}`);
  const spotifySearchUrl = `https://open.spotify.com/search/${searchQuery}`;
  const youtubeSearchUrl = `https://www.youtube.com/results?search_query=${searchQuery}`;

  return (
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
        <Music className="w-5 h-5" />
        Listen Now
      </h3>
      
      <div className="grid grid-cols-2 gap-4">
        
        <a  href={spotifySearchUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-3 px-6 py-4 bg-green-600 hover:bg-green-700 rounded-xl transition-all text-white font-semibold"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
          </svg>
          Spotify
        </a>
        
        <a
          href={youtubeSearchUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-3 px-6 py-4 bg-red-600 hover:bg-red-700 rounded-xl transition-all text-white font-semibold"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          YouTube
        </a>
      </div>
      
      <p className="text-[var(--text-tertiary)] text-xs text-center mt-4">
        Opens in new tab • External services
      </p>
    </div>
  );
};

// Main App Component
function App() {
  const [view, setView] = useState(() => sessionStorage.getItem('lyricmatch_view') || 'upload');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobId, setJobId] = useState(() => sessionStorage.getItem('lyricmatch_jobId') || null);
  const [results, setResults] = useState(() => {
    const saved = sessionStorage.getItem('lyricmatch_results');
    return saved ? JSON.parse(saved) : null;
  });
  const [progress, setProgress] = useState(() => parseInt(sessionStorage.getItem('lyricmatch_progress') || '0'));
  const [status, setStatus] = useState(() => sessionStorage.getItem('lyricmatch_status') || '');
  const [error, setError] = useState(null);
  const [currentTier, setCurrentTier] = useState(() => sessionStorage.getItem('lyricmatch_tier') || 'free');
  const [processingConfig, setProcessingConfig] = useState(() => {
    const saved = sessionStorage.getItem('lyricmatch_config');
    return saved ? JSON.parse(saved) : null;
  });
  const [showTierModal, setShowTierModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);

  const [showArtistFetch, setShowArtistFetch] = useState(false);
  
  const hasTransitionedRef = useRef(false);

  // Persist state changes
  useEffect(() => {
    sessionStorage.setItem('lyricmatch_view', view);
  }, [view]);

  useEffect(() => {
    if (jobId) sessionStorage.setItem('lyricmatch_jobId', jobId);
  }, [jobId]);

  useEffect(() => {
    if (results) sessionStorage.setItem('lyricmatch_results', JSON.stringify(results));
  }, [results]);

  useEffect(() => {
    sessionStorage.setItem('lyricmatch_progress', progress.toString());
  }, [progress]);

  useEffect(() => {
    if (status) sessionStorage.setItem('lyricmatch_status', status);
  }, [status]);

  useEffect(() => {
    sessionStorage.setItem('lyricmatch_tier', currentTier);
  }, [currentTier]);

  useEffect(() => {
    if (processingConfig) sessionStorage.setItem('lyricmatch_config', JSON.stringify(processingConfig));
  }, [processingConfig]);

  const uploadAudio = async (file, config) => {
    const formData = new FormData();
    formData.append('audio', file);
    formData.append('tier', currentTier);
    formData.append('whisper_model', config.whisper_model);
    formData.append('engine', config.engine);
    if (config.sbert_model) {
      formData.append('sbert_model', config.sbert_model);
    }
    
    const response = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Upload failed');
    }
    return response.json();
  };

  const getJobStatus = async (jobId) => {
    const response = await fetch(`http://localhost:5000/api/status/${jobId}`);
    if (!response.ok) throw new Error('Status check failed');
    return response.json();
  };

  useEffect(() => {
    if (!jobId || view !== 'processing') return;

    hasTransitionedRef.current = false;
    let pollCount = 0;
    const maxPolls = 300;

    const pollInterval = setInterval(async () => {
      try {
        pollCount++;
        
        if (pollCount > maxPolls) {
          clearInterval(pollInterval);
          setError('Processing timeout - please try again');
          setView('upload');
          return;
        }

        const statusData = await getJobStatus(jobId);
        
        const newProgress = parseInt(statusData.progress) || 0;
        setProgress(prev => Math.max(prev, newProgress));
        setStatus(statusData.status);

        if (statusData.status === 'complete') {
          if (hasTransitionedRef.current) return;
          
          hasTransitionedRef.current = true;
          clearInterval(pollInterval);
          
          if (statusData.results && Array.isArray(statusData.results) && statusData.results.length > 0) {
            const resultsData = {
              topMatch: statusData.results[0],
              alternatives: statusData.results.slice(1),
              transcription: statusData.transcription,
              language: statusData.language,
              audioInfo: statusData.audio_info,
              configUsed: statusData.config_used
            };
            
            setResults(resultsData);
            
            // FIX: Save to history BEFORE changing view
            try {
              await saveToHistory({
                filename: uploadedFile?.name || 'Unknown',
                topMatch: resultsData.topMatch,
                alternatives: resultsData.alternatives,
                transcription: resultsData.transcription,
                tier: currentTier,
                config: processingConfig
              });
              console.log('✅ Saved to history successfully');
            } catch (historyError) {
              console.error('❌ Failed to save to history:', historyError);
            }
            
            setTimeout(() => setView('results'), 500);
          } else {
            setError('No matching songs found in database');
            setTimeout(() => setView('upload'), 2000);
          }

        } else if (statusData.status === 'error') {
          clearInterval(pollInterval);
          setError(statusData.error || 'An error occurred during processing');
          setTimeout(() => setView('upload'), 2000);
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [jobId, view, uploadedFile, currentTier, processingConfig]);

  const handleFileUpload = (file) => {
    // Check file size based on tier
    const maxSize = currentTier === 'premium' ? 200 * 1024 * 1024 : 20 * 1024 * 1024;
    
    if (file.size > maxSize) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds ${maxSize / (1024 * 1024)}MB limit for ${currentTier} tier`);
      return;
    }
    
    setPendingFile(file);
    setShowConfigModal(true);
  };

  const handleStartProcessing = async (config) => {
    setShowConfigModal(false);
    
    if (!pendingFile) return;

    setUploadedFile(pendingFile);
    setProcessingConfig(config);
    setView('processing');
    setProgress(0);
    setError(null);
    setStatus('queued');
    hasTransitionedRef.current = false;

    try {
      const response = await uploadAudio(pendingFile, config);
      setJobId(response.job_id);
    } catch (err) {
      setError(err.message || 'Failed to upload file');
      setView('upload');
    }
    
    setPendingFile(null);
  };

  const handleReset = () => {
    setView('upload');
    setUploadedFile(null);
    setJobId(null);
    setResults(null);
    setProgress(0);
    setStatus('');
    setError(null);
    setProcessingConfig(null);
    hasTransitionedRef.current = false;
    
    // Clear session storage
    sessionStorage.removeItem('lyricmatch_view');
    sessionStorage.removeItem('lyricmatch_jobId');
    sessionStorage.removeItem('lyricmatch_results');
    sessionStorage.removeItem('lyricmatch_progress');
    sessionStorage.removeItem('lyricmatch_status');
    sessionStorage.removeItem('lyricmatch_config');
  };

  const handleChangeTier = () => {
    setShowTierModal(true);
  };

  const handleSelectTier = (tier) => {
    setCurrentTier(tier);
    setShowTierModal(false);
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-[var(--bg-primary)] transition-colors duration-300">
        <Header currentTier={currentTier} onChangeTier={handleChangeTier}
        setShowArtistFetch={setShowArtistFetch} />
        
        <main className="max-w-7xl mx-auto px-6 py-12">
          {error && (
            <div className="mb-8 bg-red-950/50 border border-red-800/50 rounded-2xl p-6">
              <p className="font-bold text-red-200 text-lg mb-1">Error</p>
              <p className="text-red-300 mb-4">{error}</p>
              <button 
                onClick={handleReset}
                className="px-6 py-3 bg-red-900/50 hover:bg-red-800/50 text-white rounded-lg font-semibold transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {view === 'upload' && (
            <UploadView 
              onUpload={handleFileUpload} 
              currentTier={currentTier}
              onOpenConfig={() => setShowConfigModal(true)}
            />
          )}
          {view === 'processing' && (
            <ProcessingView 
              progress={progress} 
              filename={uploadedFile?.name}
              status={status}
              tier={currentTier}
              config={processingConfig}
            />
          )}
          {view === 'results' && results && (
            <ResultsView 
              results={results} 
              onReset={handleReset}
              tier={currentTier}
              config={results.configUsed}
            />
          )}
        </main>

        <ArtistFetchModal 
          isOpen={showArtistFetch}
          onClose={() => setShowArtistFetch(false)}
          onFetch={() => {
            // Optionally refresh database stats here
            console.log('Artist fetched successfully');
          }}
        />

        <TierSelectionModal 
          isOpen={showTierModal}
          onClose={() => setShowTierModal(false)}
          onSelectTier={handleSelectTier}
        />

        <ConfigModal
          isOpen={showConfigModal}
          onClose={() => {
            setShowConfigModal(false);
            setPendingFile(null);
          }}
          onStart={handleStartProcessing}
          currentTier={currentTier}
          onChangeTier={handleChangeTier}
        />
      </div>
    </ThemeProvider>
  );
}

export default App;