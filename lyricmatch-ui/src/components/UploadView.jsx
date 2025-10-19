import React, { useState } from 'react';
import { Upload } from 'lucide-react';

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
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-white mb-3">
            Identify Your Song
          </h2>
          <p className="text-lg text-white/70">
            Upload an audio file to discover the song through lyrics recognition
          </p>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-3xl p-12 transition-all duration-300
            ${isDragging 
              ? 'border-purple-400 bg-purple-500/10 scale-105' 
              : 'border-white/20 bg-white/5 hover:bg-white/10'
            }
          `}
        >
          <div className="flex flex-col items-center gap-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Upload className="w-12 h-12 text-white" />
            </div>
            
            <div className="text-center">
              <p className="text-xl font-semibold text-white mb-2">
                Drop your audio file here
              </p>
              <p className="text-white/60">
                or click to browse
              </p>
              <p className="text-sm text-white/40 mt-3">
                Supports MP3, WAV, M4A, FLAC, OGG
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

        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="bg-white/5 rounded-xl p-4 backdrop-blur-sm">
            <div className="text-2xl font-bold text-purple-400 mb-1">Fast</div>
            <div className="text-sm text-white/60">AI-Powered</div>
          </div>
          <div className="bg-white/5 rounded-xl p-4 backdrop-blur-sm">
            <div className="text-2xl font-bold text-pink-400 mb-1">Accurate</div>
            <div className="text-sm text-white/60">Lyrics-Based</div>
          </div>
          <div className="bg-white/5 rounded-xl p-4 backdrop-blur-sm">
            <div className="text-2xl font-bold text-blue-400 mb-1">Secure</div>
            <div className="text-sm text-white/60">Private</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadView;