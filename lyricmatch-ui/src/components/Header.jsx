import React from 'react';
import { Music } from 'lucide-react';

const Header = () => {
  return (
    <header className="border-b border-white/10 backdrop-blur-xl bg-black/20">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <Music className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">LyricMatch</h1>
        </div>
        <div className="text-sm text-white/60">Audio Recognition System</div>
      </div>
    </header>
  );
};

export default Header;