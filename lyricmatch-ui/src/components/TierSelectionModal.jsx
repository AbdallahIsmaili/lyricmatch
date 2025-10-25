// src/components/TierSelectionModal.jsx
import React from 'react';
import { Zap, Crown, Check } from 'lucide-react';

export const TierSelectionModal = ({ isOpen, onClose, onSelectTier }) => {
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