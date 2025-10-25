// src/components/TierBadge.jsx
import React from 'react';
import { Crown, Zap } from 'lucide-react';

export const TierBadge = ({ tier, size = 'sm' }) => {
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