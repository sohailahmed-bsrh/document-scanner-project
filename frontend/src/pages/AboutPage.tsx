import React from 'react';
import { Info, Cpu, Layers, Sparkles, Shield, Code2, CheckCircle2 } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white">About Devsil Scanner Pro Studio</h1>
            <p className="text-xs text-slate-400">
              Commercial-Grade Classical Computer Vision Document Scanning Architecture.
            </p>
          </div>
        </div>
      </div>

      {/* Main Narrative Card */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <span>Core Computer Vision Engineering</span>
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Devsil Document Scanner Pro is engineered around classical computer vision algorithms using OpenCV, NumPy, and PIL. It contains zero external cloud neural network dependencies, ensuring 100% on-device privacy, zero latency data transmissions, and reproducible mathematical transformations.
          </p>
        </div>

        {/* Technical Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-800">
          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>4-Tier Gold-Standard Quad Detector</span>
            </h3>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Combines dynamic poly approximation, extreme 4-corner hull projections, multi-scale LAB lightness maps, and safety margin fallbacks to prevent accidental cropping of tables or text blocks.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>CamScanner Illumination Division</span>
            </h3>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Utilizes morphological background dilation and median blur estimation to divide out indoor yellow lighting shadows, outputting clean, crisp, 100% white document backgrounds.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Interactive HTML5 Canvas Quad Drag</span>
            </h3>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Custom responsive canvas renderer allowing user drag-and-drop corner adjustments with live polygon mask preview overlays and sub-pixel snapping.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>FastAPI & React 19 Architecture</span>
            </h3>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Decoupled RESTful backend API powered by Python 3, FastAPI, Uvicorn, and a high-performance React 19 + Vite + TypeScript frontend.
            </p>
          </div>
        </div>

        {/* Tech Stack Chips */}
        <div className="pt-4 border-t border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-slate-300">Technology Stack</h3>
          <div className="flex flex-wrap gap-2">
            {[
              'React 19',
              'Vite',
              'TypeScript',
              'Tailwind CSS',
              'Framer Motion',
              'FastAPI',
              'OpenCV 4.9',
              'NumPy 1.26',
              'Pillow',
              'Pydantic v2',
              'FPDF2',
              'Lucide Icons',
            ].map((tech) => (
              <span
                key={tech}
                className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-semibold text-indigo-300"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
