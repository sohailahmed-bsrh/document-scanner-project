import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Upload,
  RotateCcw,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Sliders,
  Sparkles,
  Download,
  FileText,
  Image as ImageIcon,
  CheckCircle2,
  RefreshCw,
  Copy,
  Layers,
  Sun,
  Eye,
  SlidersHorizontal,
} from 'lucide-react';
import { api } from '../services/api';
import {
  CornerDetectionResult,
  EnhancementMode,
  Point,
  ScanParameters,
  ScanProcessResult,
} from '../types/scanner';
import { ScannerCanvas } from '../components/ScannerCanvas';
import { CompareSlider } from '../components/CompareSlider';

export const ScannerPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<CornerDetectionResult | null>(null);
  const [corners, setCorners] = useState<Point[]>([]);
  const [processResult, setProcessResult] = useState<ScanProcessResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [detecting, setDetecting] = useState<boolean>(false);

  // View modes: 'crop' (interactive canvas) | 'result' (enhanced view) | 'compare' (split slider)
  const [viewMode, setViewMode] = useState<'crop' | 'result' | 'compare'>('crop');

  // Scanner parameters
  const [params, setParams] = useState<ScanParameters>({
    rotation_angle: 0,
    flip_mode: 'none',
    enhancement_mode: 'magic_color',
    brightness: 0,
    contrast: 1.0,
    sharpness: 1.2,
    warmth: 0,
    custom_name: '',
  });

  const [samples, setSamples] = useState<string[]>([]);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // Fetch dataset sample images
  useEffect(() => {
    api.getSampleImages().then((res) => {
      if (res.samples) setSamples(res.samples);
    });
  }, []);

  // Listen for Clipboard Paste (Ctrl+V)
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            handleFileSelected(file);
          }
          break;
        }
      }
    };
    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  // Handle image select & corner detection
  const handleFileSelected = async (file: File) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setProcessResult(null);
    setViewMode('crop');

    setDetecting(true);
    try {
      const res = await api.detectCorners(file);
      setDetectionResult(res);
      setCorners(res.corners);
    } catch (err) {
      console.error('Corner detection error:', err);
    } finally {
      setDetecting(false);
    }
  };

  // Drag and drop handlers
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  // Run perspective transform & enhancement scan
  const handleRunScan = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      const result = await api.processScan(selectedFile, corners, params);
      setProcessResult(result);
      setViewMode('result');
    } catch (err) {
      console.error('Scan processing error:', err);
      alert('Failed to process image scan. Please check input image format.');
    } finally {
      setLoading(false);
    }
  };

  // Reset parameters
  const handleResetCorners = () => {
    if (detectionResult) {
      setCorners(detectionResult.corners);
    }
  };

  const filterPresets: { id: EnhancementMode; label: string; desc: string }[] = [
    { id: 'magic_color', label: 'Magic Color 2.0', desc: 'CamScanner Illumination Whitening' },
    { id: 'adobe_whitening', label: 'Adobe Whitening', desc: 'Shadow Subtraction & Paper Brightening' },
    { id: 'clean_scan', label: 'Clean Scan', desc: 'Denoised Vivid Color Scan' },
    { id: 'black_and_white', label: 'Black & White', desc: 'High-Contrast B&W Threshold' },
    { id: 'ocr_friendly', label: 'OCR Friendly', desc: 'Optimized Sharp Text Binarization' },
    { id: 'grayscale', label: 'Grayscale', desc: 'Normalized Neutral Grayscale' },
    { id: 'high_contrast', label: 'High Contrast', desc: 'Bold Text Contrast Amplification' },
    { id: 'original_clean', label: 'Original Clean', desc: 'Denoised Natural Image' },
    { id: 'threshold', label: 'Otsu Threshold', desc: 'Pure Binary Thresholding' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner / Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            <span>Document Scanner Studio</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            CamScanner & Adobe Scan grade boundary detection, corner cropping, rotation, whitening & PDF suite.
          </p>
        </div>

        {selectedFile && (
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSelectedFile(null)}
              className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-xl border border-slate-700 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Process Another Image</span>
            </button>

            {processResult && (
              <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
                <button
                  onClick={() => setViewMode('result')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                    viewMode === 'result'
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Scan View
                </button>
                <button
                  onClick={() => setViewMode('compare')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                    viewMode === 'compare'
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Before/After Split
                </button>
                <button
                  onClick={() => setViewMode('crop')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                    viewMode === 'crop'
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Crop Canvas
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Scanner Workspace */}
      {!selectedFile ? (
        /* Upload & Sample Selector Area */
        <div className="space-y-6">
          <div
            ref={dropZoneRef}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-2 border-dashed border-indigo-500/30 hover:border-indigo-500 rounded-3xl p-12 text-center glass-panel bg-slate-900/40 hover:bg-slate-900/60 transition-all duration-300 cursor-pointer space-y-4 shadow-2xl"
          >
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto border border-indigo-500/20 shadow-lg shadow-indigo-500/10">
              <Upload className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <h2 className="text-lg font-bold text-white">
                Drag & Drop Document Photo Here
              </h2>
              <p className="text-xs text-slate-400">
                Supports JPG, PNG, JPEG formats up to 25 MB.
              </p>
            </div>

            <div className="flex items-center justify-center space-x-3 pt-2">
              <label className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl cursor-pointer shadow-lg shadow-indigo-500/20 transition-all">
                <span>Browse Files</span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/jpg"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileSelected(e.target.files[0]);
                    }
                  }}
                />
              </label>
              <span className="text-xs text-slate-500">or press <kbd className="px-2 py-1 bg-slate-800 text-slate-300 rounded border border-slate-700 text-[10px]">Ctrl+V</kbd> to paste</span>
            </div>
          </div>

          {/* Sample Images Section */}
          {samples.length > 0 && (
            <div className="glass-panel p-6 rounded-3xl space-y-4 border border-slate-800">
              <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
                <ImageIcon className="w-4 h-4 text-indigo-400" />
                <span>Or Select Sample Document from Dataset</span>
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {samples.map((sample) => (
                  <button
                    key={sample}
                    onClick={async () => {
                      try {
                        const res = await fetch(`/api/scans/file/${sample}`);
                        const blob = await res.blob();
                        const file = new File([blob], sample, { type: 'image/jpeg' });
                        handleFileSelected(file);
                      } catch (err) {
                        console.error('Failed to load sample:', err);
                      }
                    }}
                    className="group relative rounded-2xl bg-slate-900 border border-slate-800 p-2 hover:border-indigo-500/50 transition-all text-left"
                  >
                    <div className="aspect-video rounded-xl bg-slate-950 overflow-hidden mb-2">
                      <img
                        src={`/api/scans/file/${sample}`}
                        alt={sample}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    <p className="text-xs font-semibold text-slate-300 truncate">
                      {sample}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Document Studio Layout */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Canvas / Preview Area (2 Cols) */}
          <div className="lg:col-span-2 space-y-4">
            {detecting ? (
              <div className="glass-panel p-16 rounded-3xl text-center space-y-4 animate-pulse">
                <RefreshCw className="w-10 h-10 text-indigo-400 animate-spin mx-auto" />
                <p className="text-sm font-bold text-white">Running 4-Tier Quad Corner Detection...</p>
                <p className="text-xs text-slate-400">Analyzing document perimeters and multi-scale contours</p>
              </div>
            ) : viewMode === 'crop' && detectionResult ? (
              <ScannerCanvas
                imageSrc={previewUrl!}
                corners={corners}
                onCornersChange={(newCorners) => setCorners(newCorners)}
                originalWidth={detectionResult.width}
                originalHeight={detectionResult.height}
              />
            ) : viewMode === 'compare' && processResult ? (
              <CompareSlider
                originalSrc={processResult.original_base64}
                enhancedSrc={processResult.enhanced_base64}
              />
            ) : processResult ? (
              <div className="relative rounded-2xl overflow-hidden glass-panel border border-slate-800 p-3 shadow-2xl">
                <img
                  src={processResult.enhanced_base64}
                  alt="Scanned Output"
                  className="w-full h-auto max-h-[600px] object-contain rounded-xl block mx-auto shadow-2xl"
                />
              </div>
            ) : null}

            {/* View Result Action Buttons */}
            {processResult && (
              <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-xs font-semibold text-slate-200">
                    Scan Enhanced ({processResult.width} x {processResult.height} px)
                  </span>
                </div>

                <div className="flex items-center space-x-3">
                  <a
                    href={processResult.enhanced_base64}
                    download={params.custom_name || processResult.filename}
                    className="flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg shadow-emerald-500/20 transition-all"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Scan (JPG/PNG)</span>
                  </a>

                  <button
                    onClick={async () => {
                      try {
                        const res = await api.exportPdf([processResult.filename], params.custom_name || 'scan.pdf');
                        window.open(res.download_url, '_blank');
                      } catch (err) {
                        alert('PDF export failed.');
                      }
                    }}
                    className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg shadow-indigo-500/20 transition-all"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Export to PDF</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Scanner Control Panel (1 Col) */}
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6 shadow-xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <h3 className="font-bold text-white text-sm flex items-center space-x-2">
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <span>Scanner Control Panel</span>
                </h3>

                <button
                  onClick={handleRunScan}
                  disabled={loading}
                  className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs px-4 py-2 rounded-xl shadow-lg shadow-indigo-500/25 transition-all active:scale-95 disabled:opacity-50"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  <span>Apply & Scan</span>
                </button>
              </div>

              {/* Output Name Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Document Output Name</label>
                <input
                  type="text"
                  placeholder="e.g. Scanned_Invoice_2026.jpg"
                  value={params.custom_name}
                  onChange={(e) => setParams({ ...params, custom_name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Rotation & Flip Controls */}
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-300">Rotation & Perspective Tilt</label>
                <div className="grid grid-cols-4 gap-2">
                  <button
                    onClick={() =>
                      setParams({ ...params, rotation_angle: (params.rotation_angle - 90) % 360 })
                    }
                    className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold flex flex-col items-center justify-center"
                    title="Rotate 90° Left"
                  >
                    <RotateCcw className="w-4 h-4 mb-1 text-indigo-400" />
                    <span>↺ 90°</span>
                  </button>

                  <button
                    onClick={() =>
                      setParams({ ...params, rotation_angle: (params.rotation_angle + 90) % 360 })
                    }
                    className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold flex flex-col items-center justify-center"
                    title="Rotate 90° Right"
                  >
                    <RotateCw className="w-4 h-4 mb-1 text-indigo-400" />
                    <span>↻ 90°</span>
                  </button>

                  <button
                    onClick={() =>
                      setParams({
                        ...params,
                        flip_mode: params.flip_mode === 'horizontal' ? 'none' : 'horizontal',
                      })
                    }
                    className={`p-2 rounded-xl border text-xs font-semibold flex flex-col items-center justify-center transition-colors ${
                      params.flip_mode === 'horizontal'
                        ? 'bg-indigo-600 text-white border-indigo-500'
                        : 'bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-300'
                    }`}
                    title="Flip Horizontal"
                  >
                    <FlipHorizontal className="w-4 h-4 mb-1" />
                    <span>Flip H</span>
                  </button>

                  <button
                    onClick={() =>
                      setParams({
                        ...params,
                        flip_mode: params.flip_mode === 'vertical' ? 'none' : 'vertical',
                      })
                    }
                    className={`p-2 rounded-xl border text-xs font-semibold flex flex-col items-center justify-center transition-colors ${
                      params.flip_mode === 'vertical'
                        ? 'bg-indigo-600 text-white border-indigo-500'
                        : 'bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-300'
                    }`}
                    title="Flip Vertical"
                  >
                    <FlipVertical className="w-4 h-4 mb-1" />
                    <span>Flip V</span>
                  </button>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Fine Tilt Angle</span>
                    <span>{params.rotation_angle}°</span>
                  </div>
                  <input
                    type="range"
                    min="-45"
                    max="45"
                    value={params.rotation_angle}
                    onChange={(e) =>
                      setParams({ ...params, rotation_angle: parseFloat(e.target.value) })
                    }
                    className="w-full accent-indigo-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>
              </div>

              {/* Primary Enhancement Preset Filter Picker */}
              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-300">Active Enhancement Preset</label>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {filterPresets.map((preset) => {
                    const isSelected = params.enhancement_mode === preset.id;
                    return (
                      <button
                        key={preset.id}
                        onClick={() => setParams({ ...params, enhancement_mode: preset.id })}
                        className={`w-full p-2.5 rounded-xl border text-left transition-all ${
                          isSelected
                            ? 'bg-indigo-600/20 border-indigo-500 text-white'
                            : 'bg-slate-900/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/60'
                        }`}
                      >
                        <p className="text-xs font-bold">{preset.label}</p>
                        <p className="text-[10px] text-slate-400">{preset.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Adobe Scan Fine-Tuning Sliders */}
              <div className="space-y-3 pt-2 border-t border-slate-800">
                <label className="text-xs font-semibold text-slate-300 flex items-center space-x-2">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Fine-Tuning Adjustments</span>
                </label>

                {/* Brightness */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Brightness</span>
                    <span>{params.brightness}</span>
                  </div>
                  <input
                    type="range"
                    min="-100"
                    max="100"
                    value={params.brightness}
                    onChange={(e) =>
                      setParams({ ...params, brightness: parseInt(e.target.value) })
                    }
                    className="w-full accent-indigo-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Contrast */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Contrast</span>
                    <span>{params.contrast}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.5"
                    step="0.1"
                    value={params.contrast}
                    onChange={(e) =>
                      setParams({ ...params, contrast: parseFloat(e.target.value) })
                    }
                    className="w-full accent-indigo-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Sharpness */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Text Sharpness</span>
                    <span>{params.sharpness}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="3.0"
                    step="0.2"
                    value={params.sharpness}
                    onChange={(e) =>
                      setParams({ ...params, sharpness: parseFloat(e.target.value) })
                    }
                    className="w-full accent-indigo-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Warmth */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium">
                    <span>Color Temperature (Warmth)</span>
                    <span>{params.warmth}</span>
                  </div>
                  <input
                    type="range"
                    min="-50"
                    max="50"
                    value={params.warmth}
                    onChange={(e) =>
                      setParams({ ...params, warmth: parseInt(e.target.value) })
                    }
                    className="w-full accent-indigo-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>
              </div>

              {/* Reset Corner Controls */}
              <div className="pt-2 border-t border-slate-800">
                <button
                  onClick={handleResetCorners}
                  className="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800 transition-colors"
                >
                  Reset Corners to Auto-Detected
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
