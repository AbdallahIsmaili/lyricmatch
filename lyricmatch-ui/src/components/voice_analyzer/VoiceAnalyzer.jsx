import React, { useState } from 'react';
import { Mic, Upload, User, Activity, Music, AlertCircle } from 'lucide-react';
import { analyzeVoice } from '../../utils/api';

export const VoiceAnalyzerPage = () => {
  const [view, setView] = useState('upload'); // upload, processing, results
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

    const handleFileUpload = async (uploadedFile) => {
    setFile(uploadedFile);
    setView('processing');
    setLoading(true);
    setError(null);

    try {
        const data = await analyzeVoice(uploadedFile); // ✅ This already handles FormData internally
        
        if (data.error) {
        setError(data.error);
        setView('upload');
        } else {
        setAnalysis(data);
        setView('results');
        }
    } catch (err) {
        setError(err.message || 'Analysis failed');
        setView('upload');
    } finally {
        setLoading(false);
    }
    };

  const handleReset = () => {
    setView('upload');
    setFile(null);
    setAnalysis(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <div className="border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
              <Mic className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-[var(--text-primary)]">Voice Analyzer</h1>
              <p className="text-[var(--text-secondary)] text-lg">Analyze speaker characteristics from audio</p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
              <span className="text-sm text-[var(--text-secondary)]">Gender Detection</span>
            </div>
            <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
              <span className="text-sm text-[var(--text-secondary)]">Age Estimation</span>
            </div>
            <div className="px-4 py-2 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg">
              <span className="text-sm text-[var(--text-secondary)]">Speaker Counting</span>
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {error && (
          <div className="mb-6 bg-red-950/50 border border-red-800/50 rounded-2xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <p className="font-bold text-red-200 text-lg mb-1">Analysis Error</p>
              <p className="text-red-300">{error}</p>
            </div>
          </div>
        )}

        {view === 'upload' && <UploadView onUpload={handleFileUpload} />}
        {view === 'processing' && <ProcessingView filename={file?.name} />}
        {view === 'results' && analysis && (
          <ResultsView analysis={analysis} onReset={handleReset} />
        )}
      </main>
    </div>
  );
};

const UploadView = ({ onUpload }) => {
  const [isDragging, setIsDragging] = useState(false);

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
    if (file) onUpload(file);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-20 transition-all ${
          isDragging 
            ? 'border-purple-500 bg-purple-500/10' 
            : 'border-[var(--border)] bg-[var(--bg-secondary)] hover:border-purple-500/50'
        }`}
      >
        <div className="flex flex-col items-center gap-6">
          <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
            <Mic className="w-12 h-12 text-white" />
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[var(--text-primary)] mb-2">Upload Audio for Voice Analysis</p>
            <p className="text-[var(--text-secondary)]">Drop your file here or click to browse</p>
          </div>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
        </div>
      </div>

      <div className="mt-12 grid grid-cols-3 gap-6">
        <Feature icon={User} title="Gender Detection" desc="Male/Female classification" />
        <Feature icon={Activity} title="Pitch Analysis" desc="Fundamental frequency" />
        <Feature icon={Music} title="Voice Quality" desc="Recording assessment" />
      </div>
    </div>
  );
};

const Feature = ({ icon: Icon, title, desc }) => (
  <div className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border)]">
    <Icon className="w-8 h-8 text-purple-500 mb-3" />
    <div className="text-lg font-bold text-[var(--text-primary)] mb-1">{title}</div>
    <div className="text-sm text-[var(--text-secondary)]">{desc}</div>
  </div>
);

const ProcessingView = ({ filename }) => (
  <div className="max-w-4xl mx-auto text-center">
    <div className="mb-8">
      <div className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full animate-pulse mb-6">
        <Activity className="w-16 h-16 text-white" />
      </div>
      <h2 className="text-4xl font-bold text-[var(--text-primary)] mb-2">Analyzing Voice...</h2>
      <p className="text-[var(--text-secondary)] text-lg">{filename}</p>
    </div>
    <div className="bg-[var(--bg-secondary)] rounded-2xl p-8 border border-[var(--border)]">
      <div className="space-y-4">
        {['Detecting speech segments', 'Extracting pitch features', 'Analyzing gender', 'Estimating age'].map((step, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="w-4 h-4 rounded-full bg-purple-500 animate-pulse" />
            <span className="text-[var(--text-primary)]">{step}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);


const ResultsView = ({ analysis, onReset }) => {
  const gender = analysis.analysis?.gender || {};
  const age = analysis.analysis?.age || {};
  const speakers = analysis.analysis?.speaker_count || {};
  const quality = analysis.analysis?.voice_quality || {};

  // Handle multi-speaker vs single speaker display
  const isMultiSpeaker = gender.multi_speaker === true;
  const speakerAnalyses = speakers.speaker_analyses || {};

  // For voice characteristics - use first valid speaker's data
  let voiceCharData = gender;
  if (isMultiSpeaker && Object.keys(speakerAnalyses).length > 0) {
    // Find first speaker with valid data
    for (const [speakerId, analysis] of Object.entries(speakerAnalyses)) {
      if (analysis.gender?.classification !== 'unknown') {
        voiceCharData = analysis.gender;
        break;
      }
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-3xl p-8">
        <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-6">Analysis Results</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <StatCard
            title="Gender"
            value={gender.classification?.toUpperCase() || 'UNKNOWN'}
            subtitle={`${Math.round((gender.confidence || 0) * 100)}% confidence`}
            icon={User}
            badge={isMultiSpeaker ? 'Multi-Speaker' : null}
          />
          <StatCard
            title="Estimated Age"
            value={age.estimated_age ? `~${age.estimated_age}` : 'N/A'}
            subtitle={age.age_range || 'Unknown range'}
            icon={Activity}
          />
          <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)] col-span-full">
            <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <Music className="w-5 h-5 text-purple-500" />
              Speaker Detection
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="text-3xl font-bold text-[var(--text-primary)] mb-2">
                  {speakers.estimated_count || '?'} Speaker{speakers.estimated_count !== 1 ? 's' : ''}
                </div>
                <div className="text-sm text-[var(--text-secondary)] mb-4">
                  Confidence: {speakers.confidence || 'low'} • Method: {speakers.method || 'N/A'}
                </div>
                
                {speakers.overlapping_segments > 0 && (
                  <div className="px-4 py-2 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                    <span className="text-orange-500 text-sm font-bold">
                      📊 {speakers.overlapping_segments} overlapping speech segments detected
                    </span>
                  </div>
                )}
              </div>
              
              {/* Enhanced speaker breakdown with gender */}
              {Object.keys(speakerAnalyses).length > 0 && (
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-tertiary)] mb-3">Per-Speaker Analysis:</h4>
                  {Object.entries(speakerAnalyses).map(([speaker, data]) => {
                    const genderLabel = data.gender?.classification || 'unknown';
                    const genderConf = data.gender?.confidence || 0;
                    const duration = data.duration || 0;
                    
                    return (
                      <div key={speaker} className="mb-3 p-3 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border)]">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-[var(--text-primary)] font-semibold">{speaker}</span>
                          <span className="text-[var(--text-secondary)] font-mono text-sm">{duration.toFixed(1)}s</span>
                        </div>
                        <div className="text-sm text-[var(--text-secondary)]">
                          {genderLabel !== 'unknown' ? (
                            <>
                              <span className="capitalize">{genderLabel}</span> ({Math.round(genderConf * 100)}%)
                            </>
                          ) : (
                            <span className="text-yellow-500">Gender unknown</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              
              {/* Fallback to speaker durations if no per-speaker analysis */}
              {Object.keys(speakerAnalyses).length === 0 && speakers.speaker_durations && (
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-tertiary)] mb-2">Speaking Time:</h4>
                  {Object.entries(speakers.speaker_durations).map(([speaker, duration]) => (
                    <div key={speaker} className="flex justify-between items-center mb-2">
                      <span className="text-[var(--text-primary)]">{speaker}:</span>
                      <span className="text-[var(--text-secondary)] font-mono">{duration.toFixed(1)}s</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Voice Characteristics */}
        <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Voice Characteristics</h3>
          <div className="space-y-4">
            <DataRow 
              label="Mean Pitch" 
              value={voiceCharData.mean_f0 ? `${voiceCharData.mean_f0.toFixed(1)} Hz` : 'N/A'} 
            />
            <DataRow 
              label="Pitch Range (IQR)" 
              value={voiceCharData.f0_iqr ? `${voiceCharData.f0_iqr.toFixed(1)} Hz` : 'N/A'} 
            />
            <DataRow 
              label="Sample Count" 
              value={voiceCharData.sample_count || 'N/A'} 
            />
            <DataRow 
              label="Analysis Method" 
              value={voiceCharData.method || 'N/A'} 
            />
            {isMultiSpeaker && (
              <div className="pt-3 border-t border-[var(--border)]">
                <p className="text-xs text-[var(--text-tertiary)] italic">
                  * Showing data from primary speaker
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recording Quality */}
        <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Recording Quality</h3>
          <div className="space-y-4">
            <DataRow label="Assessment" value={quality.assessment?.toUpperCase() || 'N/A'} />
            <DataRow label="Quality Score" value={`${Math.round((quality.quality_score || 0) * 100)}%`} />
            <DataRow label="SNR Estimate" value={`${quality.snr_estimate?.toFixed(1) || 'N/A'} dB`} />
            <DataRow label="Clarity" value={`${Math.round((quality.clarity || 0) * 100)}%`} />
          </div>
        </div>
      </div>

      {/* Summary Text */}
      {analysis.summary && (
        <div className="bg-[var(--bg-secondary)] rounded-2xl p-6 border border-[var(--border)]">
          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-4">Summary</h3>
          <pre className="text-[var(--text-secondary)] whitespace-pre-wrap font-mono text-sm">
            {analysis.summary}
          </pre>
        </div>
      )}

      <button
        onClick={onReset}
        className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:opacity-90 transition-opacity"
      >
        Analyze Another Audio
      </button>
    </div>
  );
};

// Updated StatCard to support badge
const StatCard = ({ title, value, subtitle, icon: Icon, badge }) => (
  <div className="bg-[var(--bg-primary)] rounded-xl p-6 border border-[var(--border)] relative">
    {badge && (
      <div className="absolute top-2 right-2 px-2 py-1 bg-purple-500/20 border border-purple-500/50 rounded text-xs text-purple-300">
        {badge}
      </div>
    )}
    <Icon className="w-8 h-8 text-purple-500 mb-3" />
    <div className="text-sm text-[var(--text-tertiary)] mb-1">{title}</div>
    <div className="text-3xl font-bold text-[var(--text-primary)] mb-1">{value}</div>
    <div className="text-sm text-[var(--text-secondary)]">{subtitle}</div>
  </div>
);

const DataRow = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-[var(--text-tertiary)]">{label}:</span>
    <span className="text-[var(--text-primary)] font-semibold">{value}</span>
  </div>
);