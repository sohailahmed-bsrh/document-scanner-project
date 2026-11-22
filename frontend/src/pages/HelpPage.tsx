import React from 'react';
import { HelpCircle, Keyboard, Lightbulb, CheckCircle2, FileQuestion } from 'lucide-react';

export const HelpPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white">Help & User Guide</h1>
            <p className="text-xs text-slate-400">
              Keyboard shortcuts reference, scanning tips, and feature documentation.
            </p>
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts Card */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Keyboard className="w-4 h-4 text-indigo-400" />
          <span>Keyboard Shortcuts Reference</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { key: 'Ctrl + V', action: 'Paste document photo directly from clipboard' },
            { key: 'Drag & Drop', action: 'Drop document image file onto upload area' },
            { key: 'Click & Drag Dots', action: 'Adjust Top-Left, Top-Right, Bottom-Right, Bottom-Left corners' },
            { key: 'Before/After Slider', action: 'Drag middle split bar to inspect document enhancement' },
          ].map((item, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800"
            >
              <span className="text-xs text-slate-300 font-medium">{item.action}</span>
              <kbd className="px-2.5 py-1 bg-slate-800 text-indigo-300 font-mono text-[11px] font-bold rounded-lg border border-slate-700">
                {item.key}
              </kbd>
            </div>
          ))}
        </div>
      </div>

      {/* Scanning Best Practices */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span>Best Practices for Optimal Scan Quality</span>
        </h2>

        <div className="space-y-3">
          {[
            {
              title: 'High Contrast Background',
              desc: 'Place white document paper on dark tables or surfaces for 100% boundary detection accuracy.',
            },
            {
              title: 'Avoid Severe Overhead Shadows',
              desc: 'While Magic Color 2.0 effectively divides shadows, holding your camera at a slight angle prevents hard phone hand shadows.',
            },
            {
              title: 'Use Magic Color 2.0 for Documents',
              desc: 'Magic Color 2.0 whitens paper background to 100% while keeping signatures, stamps, and colored headers intact.',
            },
            {
              title: 'Use B&W / OCR Mode for Printing',
              desc: 'Use Black & White or OCR Friendly modes when generating clean scans for printed text or archival storage.',
            },
          ].map((tip, idx) => (
            <div key={idx} className="flex items-start space-x-3 p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-white">{tip.title}</p>
                <p className="text-[11px] text-slate-400">{tip.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
