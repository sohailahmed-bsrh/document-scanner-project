import React, { useEffect, useRef, useState } from 'react';
import { Point } from '../types/scanner';
import { RotateCw, RefreshCw, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface ScannerCanvasProps {
  imageSrc: string;
  corners: Point[];
  onCornersChange: (corners: Point[]) => void;
  originalWidth: number;
  originalHeight: number;
}

export const ScannerCanvas: React.FC<ScannerCanvasProps> = ({
  imageSrc,
  corners,
  onCornersChange,
  originalWidth,
  originalHeight,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [activeCorner, setActiveCorner] = useState<number | null>(null);
  const [zoom, setZoom] = useState<number>(1);
  const [imgElement, setImgElement] = useState<HTMLImageElement | null>(null);

  // Load image element
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageSrc;
    img.onload = () => {
      setImgElement(img);
    };
  }, [imageSrc]);

  // Redraw canvas whenever corners, image, or zoom changes
  useEffect(() => {
    if (!canvasRef.current || !containerRef.current || !imgElement) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const containerWidth = containerRef.current.clientWidth;
    const scale = containerWidth / (originalWidth || imgElement.naturalWidth || 800);
    const displayWidth = containerWidth;
    const displayHeight = (originalHeight || imgElement.naturalHeight || 600) * scale;

    canvas.width = displayWidth;
    canvas.height = displayHeight;

    // Clear
    ctx.clearRect(0, 0, displayWidth, displayHeight);

    // Draw background image
    ctx.drawImage(imgElement, 0, 0, displayWidth, displayHeight);

    if (corners.length === 4) {
      // Scale corners to display dimensions
      const displayCorners: Point[] = corners.map(([x, y]) => [x * scale, y * scale]);

      // Draw semi-transparent polygon mask outside the corners
      ctx.fillStyle = 'rgba(99, 102, 241, 0.15)';
      ctx.beginPath();
      ctx.moveTo(displayCorners[0][0], displayCorners[0][1]);
      ctx.lineTo(displayCorners[1][0], displayCorners[1][1]);
      ctx.lineTo(displayCorners[2][0], displayCorners[2][1]);
      ctx.lineTo(displayCorners[3][0], displayCorners[3][1]);
      ctx.closePath();
      ctx.fill();

      // Draw bounding lines
      ctx.strokeStyle = '#6366f1';
      ctx.lineWidth = 3;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(displayCorners[0][0], displayCorners[0][1]);
      ctx.lineTo(displayCorners[1][0], displayCorners[1][1]);
      ctx.lineTo(displayCorners[2][0], displayCorners[2][1]);
      ctx.lineTo(displayCorners[3][0], displayCorners[3][1]);
      ctx.closePath();
      ctx.stroke();

      // Corner colors & labels
      const cornerLabels = ['TL', 'TR', 'BR', 'BL'];
      const cornerColors = ['#ef4444', '#eab308', '#3b82f6', '#10b981'];

      displayCorners.forEach(([cx, cy], idx) => {
        const isHovered = activeCorner === idx;
        const radius = isHovered ? 14 : 10;

        // Outer glow
        ctx.beginPath();
        ctx.arc(cx, cy, radius + 4, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.fill();

        // Inner circle
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
        ctx.fillStyle = cornerColors[idx];
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label tag
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(cornerLabels[idx], cx, cy);
      });
    }
  }, [imgElement, corners, activeCorner, originalWidth, originalHeight]);

  // Handle pointer dragging
  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || corners.length !== 4) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const scale = rect.width / (originalWidth || 800);
    const clickX = (e.clientX - rect.left) / scale;
    const clickY = (e.clientY - rect.top) / scale;

    // Find closest corner within radius threshold
    let closestIdx = -1;
    let minDistance = 40 / scale; // 40px hit area

    corners.forEach(([cx, cy], idx) => {
      const dist = Math.hypot(cx - clickX, cy - clickY);
      if (dist < minDistance) {
        minDistance = dist;
        closestIdx = idx;
      }
    });

    if (closestIdx !== -1) {
      setActiveCorner(closestIdx);
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    }
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (activeCorner === null || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const scale = rect.width / (originalWidth || 800);

    let newX = Math.max(0, Math.min(originalWidth, (e.clientX - rect.left) / scale));
    let newY = Math.max(0, Math.min(originalHeight, (e.clientY - rect.top) / scale));

    const updatedCorners = [...corners] as Point[];
    updatedCorners[activeCorner] = [Math.round(newX), Math.round(newY)];
    onCornersChange(updatedCorners);
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (activeCorner !== null) {
      setActiveCorner(null);
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    }
  };

  return (
    <div className="relative w-full rounded-2xl overflow-hidden glass-panel border border-slate-800 p-3">
      {/* Canvas Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-900/80 rounded-xl mb-3 border border-slate-800 text-xs font-medium text-slate-300">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
          <span>Interactive Quad Crop Engine</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-slate-400">
            {originalWidth} x {originalHeight} px
          </span>
          <button
            onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
            className="p-1 hover:bg-slate-800 rounded transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="w-8 text-center">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(2.5, z + 0.25))}
            className="p-1 hover:bg-slate-800 rounded transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Canvas Display Area */}
      <div
        ref={containerRef}
        className="relative w-full overflow-auto max-h-[600px] flex items-center justify-center rounded-xl bg-slate-950"
      >
        <div style={{ transform: `scale(${zoom})`, transformOrigin: 'center top' }} className="transition-transform duration-150">
          <canvas
            ref={canvasRef}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            className="cursor-crosshair rounded-lg block shadow-2xl"
          />
        </div>
      </div>

      {/* Instruction Badge */}
      <div className="mt-2 text-center text-xs text-slate-400">
        💡 Drag the 4 corner dots (<span className="text-red-400 font-semibold">TL</span>, <span className="text-amber-400 font-semibold">TR</span>, <span className="text-blue-400 font-semibold">BR</span>, <span className="text-emerald-400 font-semibold">BL</span>) to align document edges precisely.
      </div>
    </div>
  );
};
