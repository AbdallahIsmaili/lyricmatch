// src/components/UploadView.jsx
import React, { useState } from 'react';
import { Upload, Sparkles, Zap, Shield, Settings, Activity } from 'lucide-react';
import { TierBadge } from './TierBadge';
import { AudioRecorder } from './AudioRecorder';

export const UploadView = ({ onUpload, currentTier, onOpenConfig }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');

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