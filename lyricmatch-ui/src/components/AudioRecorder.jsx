// src/components/AudioRecorder.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Activity, Crown } from 'lucide-react';

export const AudioRecorder = ({ onRecordingComplete, currentTier }) => {
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

  const maxDuration = currentTier === 'premium' ? 120 : 30;

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

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

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
        
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setDuration(0);

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