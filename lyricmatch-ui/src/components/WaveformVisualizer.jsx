// src/components/WaveformVisualizer.jsx
import React, { useRef, useEffect } from 'react';

export const WaveformVisualizer = ({ isActive }) => {
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