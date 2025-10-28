// src/components/WaveformVisualizer.jsx
import React, { useRef, useEffect } from 'react';

export const WaveformVisualizer = ({ isActive, fullscreen = false }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const wavesRef = useRef([]);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width;
    let height = canvas.height;

    // Initialize multiple wave layers with different properties
    if (wavesRef.current.length === 0) {
      wavesRef.current = [
        { amplitude: 40, frequency: 0.015, speed: 0.02, offset: 0, opacity: 0.15, color: [99, 102, 241] },
        { amplitude: 60, frequency: 0.012, speed: 0.015, offset: Math.PI / 3, opacity: 0.12, color: [139, 92, 246] },
        { amplitude: 50, frequency: 0.018, speed: 0.025, offset: Math.PI * 2 / 3, opacity: 0.1, color: [168, 85, 247] },
        { amplitude: 70, frequency: 0.01, speed: 0.018, offset: Math.PI, opacity: 0.08, color: [192, 132, 252] },
        { amplitude: 55, frequency: 0.02, speed: 0.022, offset: Math.PI * 4 / 3, opacity: 0.1, color: [147, 51, 234] },
      ];
    }

    const drawWave = (wave, time) => {
      ctx.beginPath();
      ctx.moveTo(0, height / 2);

      const points = [];
      const resolution = fullscreen ? 3 : 5;
      
      for (let x = 0; x <= width; x += resolution) {
        // Multiple sine waves for organic movement
        const y1 = Math.sin(x * wave.frequency + time * wave.speed + wave.offset) * wave.amplitude;
        const y2 = Math.sin(x * wave.frequency * 1.5 - time * wave.speed * 0.8 + wave.offset) * wave.amplitude * 0.5;
        const y3 = Math.sin(x * wave.frequency * 0.5 + time * wave.speed * 1.2 + wave.offset) * wave.amplitude * 0.3;
        
        const y = height / 2 + (isActive ? (y1 + y2 + y3) : (y1 + y2 + y3) * 0.2);
        
        points.push({ x, y });
      }

      // Draw smooth curve through points
      for (let i = 0; i < points.length - 1; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
      }

      // Create gradient fill
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      const [r, g, b] = wave.color;
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0)`);
      gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${wave.opacity})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

      ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${wave.opacity * 1.5})`;
      ctx.lineWidth = fullscreen ? 2.5 : 2;
      ctx.stroke();

      // Fill area under wave
      ctx.lineTo(width, height);
      ctx.lineTo(0, height);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();
    };

    const animate = () => {
      // Clear with slight trail effect for smoother motion
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, width, height);

      if (isActive) {
        timeRef.current += 0.8;
      } else {
        timeRef.current += 0.2;
      }

      // Draw waves from back to front
      wavesRef.current.forEach(wave => {
        drawWave(wave, timeRef.current);
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, fullscreen]);

  if (fullscreen) {
    return (
      <canvas
        ref={canvasRef}
        width={1920}
        height={1080}
        className="fixed inset-0 w-full h-full opacity-40"
        style={{ mixBlendMode: 'screen' }}
      />
    );
  }

  return (
    <canvas
      ref={canvasRef}
      width={1200}
      height={200}
      className="w-full h-32 rounded-xl"
    />
  );
};