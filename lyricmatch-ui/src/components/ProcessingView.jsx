import React from 'react';
import { Loader2 } from 'lucide-react';

const ProcessingView = ({ progress, filename, status }) => {
  // Ensure progress is a valid number
  const safeProgress = Math.min(100, Math.max(0, parseInt(progress) || 0));
  
  const stages = {
    'queued': { name: 'Queued', color: 'text-blue-400' },
    'preprocessing': { name: 'Preprocessing Audio', color: 'text-purple-400' },
    'transcribing': { name: 'Transcribing Lyrics', color: 'text-pink-400' },
    'matching': { name: 'Matching Database', color: 'text-green-400' },
    'complete': { name: 'Complete!', color: 'text-emerald-400' }
  };

  const currentStage = stages[status] || stages['queued'];

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-2">
            Analyzing Audio
          </h2>
          <p className="text-white/60">{filename}</p>
        </div>

        {/* Large Circular Spinner */}
        <div className="flex justify-center mb-12">
          <div className="relative w-64 h-64">
            {/* Background Circle */}
            <svg className="w-64 h-64 transform -rotate-90">
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-white/10"
              />
              {/* Progress Circle */}
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="url(#gradient)"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 120}`}
                strokeDashoffset={`${2 * Math.PI * 120 * (1 - safeProgress / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-500 ease-out"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
            </svg>

            {/* Center Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Loader2 className={`w-16 h-16 ${currentStage.color} animate-spin mb-3`} />
              <div className="text-5xl font-bold text-white mb-1">
                {Math.round(safeProgress)}%
              </div>
              <div className={`${currentStage.color} font-semibold`}>
                {currentStage.name}
              </div>
            </div>
          </div>
        </div>

        {/* Processing Stages */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <div className="space-y-4">
            {Object.entries(stages).map(([key, stage]) => {
              const isActive = key === status;
              const threshold = {
                'queued': 0,
                'preprocessing': 10,
                'transcribing': 30,
                'matching': 70,
                'complete': 100
              }[key];
              const isCompleted = safeProgress > threshold;

              return (
                <div 
                  key={key}
                  className={`flex items-center gap-3 transition-all duration-300 ${
                    isActive ? 'scale-105' : ''
                  }`}
                >
                  <div className={`
                    w-3 h-3 rounded-full transition-all duration-300
                    ${isCompleted ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-white/20'}
                    ${isActive ? 'animate-pulse' : ''}
                  `} />
                  <div className={`
                    flex-1 font-medium transition-colors duration-300
                    ${isActive ? stage.color : isCompleted ? 'text-white/80' : 'text-white/40'}
                  `}>
                    {stage.name}
                  </div>
                  {isCompleted && !isActive && (
                    <div className="text-green-400">✓</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingView;