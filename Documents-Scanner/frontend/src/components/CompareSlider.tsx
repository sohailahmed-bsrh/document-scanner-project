import React, { useState } from 'react';

interface CompareSliderProps {
  originalSrc: string;
  enhancedSrc: string;
}

export const CompareSlider: React.FC<CompareSliderProps> = ({ originalSrc, enhancedSrc }) => {
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleMove = (clientX: number, rect: DOMRect) => {
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(percentage);
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(true);
    const rect = e.currentTarget.getBoundingClientRect();
    handleMove(e.clientX, rect);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    handleMove(e.clientX, rect);
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  return (
    <div
      className="relative w-full max-h-[600px] overflow-hidden rounded-2xl border border-slate-800 shadow-2xl select-none cursor-ew-resize glass-panel"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
    >
      {/* Enhanced Image (Background Layer) */}
      <img
        src={enhancedSrc}
        alt="Enhanced Scan"
        className="w-full h-auto max-h-[600px] object-contain block mx-auto pointer-events-none"
      />
      <div className="absolute top-3 right-3 bg-indigo-600/90 text-white text-[10px] font-bold px-2.5 py-1 rounded-md tracking-wider uppercase backdrop-blur-md shadow-lg pointer-events-none">
        Enhanced Scan
      </div>

      {/* Original Image (Clipped Overlay Layer) */}
      <div
        className="absolute top-0 left-0 bottom-0 overflow-hidden pointer-events-none"
        style={{ width: `${sliderPos}%` }}
      >
        <img
          src={originalSrc}
          alt="Original Photo"
          className="w-full h-auto max-h-[600px] object-contain block mx-auto max-w-none pointer-events-none"
          style={{ width: '100%' }}
        />
        <div className="absolute top-3 left-3 bg-slate-800/90 text-slate-200 text-[10px] font-bold px-2.5 py-1 rounded-md tracking-wider uppercase backdrop-blur-md shadow-lg">
          Original Photo
        </div>
      </div>

      {/* Splitter Line & Handle */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_10px_rgba(0,0,0,0.8)] pointer-events-none"
        style={{ left: `${sliderPos}%` }}
      >
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white text-slate-900 shadow-xl flex items-center justify-center font-bold text-xs border-2 border-indigo-600">
          ↔
        </div>
      </div>
    </div>
  );
};
