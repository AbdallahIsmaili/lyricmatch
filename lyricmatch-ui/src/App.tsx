// src/App.tsx
import React, { useState, useEffect, useRef } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/Header';
import { TierSelectionModal } from './components/TierSelectionModal';
import { ConfigModal } from './components/ConfigModal';
import { ArtistFetchModal } from './components/ArtistFetchModal';
import { UploadView } from './components/UploadView';
import { ProcessingView } from './components/ProcessingView';
import { ResultsView } from './components/ResultsView';
import { uploadAudio, getJobStatus } from './utils/api';
import { saveToHistory } from './utils/db';
import './styles/theme.css';

function App() {
  const [view, setView] = useState(() => sessionStorage.getItem('waveseek_view') || 'upload');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobId, setJobId] = useState(() => sessionStorage.getItem('waveseek_jobId') || null);
  const [results, setResults] = useState(() => {
    const saved = sessionStorage.getItem('waveseek_results');
    return saved ? JSON.parse(saved) : null;
  });
  const [progress, setProgress] = useState(() => parseInt(sessionStorage.getItem('waveseek_progress') || '0'));
  const [status, setStatus] = useState(() => sessionStorage.getItem('waveseek_status') || '');
  const [error, setError] = useState(null);
  const [currentTier, setCurrentTier] = useState(() => sessionStorage.getItem('waveseek_tier') || 'free');
  const [processingConfig, setProcessingConfig] = useState(() => {
    const saved = sessionStorage.getItem('waveseek_config');
    return saved ? JSON.parse(saved) : null;
  });
  const [showTierModal, setShowTierModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showArtistFetch, setShowArtistFetch] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  
  const hasTransitionedRef = useRef(false);

  // Persist state changes
  useEffect(() => {
    sessionStorage.setItem('waveseek_view', view);
  }, [view]);

  useEffect(() => {
    if (jobId) sessionStorage.setItem('waveseek_jobId', jobId);
  }, [jobId]);

  useEffect(() => {
    if (results) sessionStorage.setItem('waveseek_results', JSON.stringify(results));
  }, [results]);

  useEffect(() => {
    sessionStorage.setItem('waveseek_progress', progress.toString());
  }, [progress]);

  useEffect(() => {
    if (status) sessionStorage.setItem('waveseek_status', status);
  }, [status]);

  useEffect(() => {
    sessionStorage.setItem('waveseek_tier', currentTier);
  }, [currentTier]);

  useEffect(() => {
    if (processingConfig) sessionStorage.setItem('waveseek_config', JSON.stringify(processingConfig));
  }, [processingConfig]);

  // Poll job status
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
            
            try {
              await saveToHistory({
                filename: uploadedFile?.name || 'Unknown',
                topMatch: resultsData.topMatch,
                alternatives: resultsData.alternatives,
                transcription: resultsData.transcription,
                tier: currentTier,
                config: processingConfig
              });
            } catch (historyError) {
              console.error('Failed to save to history:', historyError);
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
      const response = await uploadAudio(pendingFile, config, currentTier);
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
    
    sessionStorage.removeItem('waveseek_view');
    sessionStorage.removeItem('waveseek_jobId');
    sessionStorage.removeItem('waveseek_results');
    sessionStorage.removeItem('waveseek_progress');
    sessionStorage.removeItem('waveseek_status');
    sessionStorage.removeItem('waveseek_config');
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
        <Header 
          currentTier={currentTier} 
          onChangeTier={handleChangeTier}
          setShowArtistFetch={setShowArtistFetch} 
        />
        
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