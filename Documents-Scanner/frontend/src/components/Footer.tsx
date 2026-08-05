import React from 'react';
import { ShieldCheck, Cpu, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="glass-panel border-t border-slate-800/80 px-4 lg:px-8 py-6 mt-12 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <p className="font-semibold text-slate-200">Devsil Document Scanner Pro Studio</p>
            <p className="text-[11px] text-slate-500">
              Classical CV Engine (OpenCV, NumPy, FastAPI, React 19)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-[11px] text-slate-400">
          <span className="flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>100% On-Premise Data Privacy</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Illumination Whitening Engine v2.0</span>
          </span>
        </div>

        <p className="text-[11px] text-slate-500">
          © 2026 Devsil Document Scanner. Production Commercial Release.
        </p>
      </div>
    </footer>
  );
};
