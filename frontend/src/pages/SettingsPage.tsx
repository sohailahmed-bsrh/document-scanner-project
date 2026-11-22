import React, { useState } from 'react';
import { Settings, Moon, Sun, Sliders, FileText, Monitor, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [defaultResolution, setDefaultResolution] = useState<number>(800);
  const [defaultFilter, setDefaultFilter] = useState<string>('magic_color');
  const [defaultPdfFormat, setDefaultPdfFormat] = useState<string>('A4');

  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center space-x-2">
            <Settings className="w-6 h-6 text-indigo-400" />
            <span>Scanner Studio Settings</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure default processing resolutions, theme modes, PDF export preferences, and filter defaults.
          </p>
        </div>

        {saved && (
          <div className="flex items-center space-x-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold px-4 py-2 rounded-xl">
            <Check className="w-4 h-4" />
            <span>Preferences Saved</span>
          </div>
        )}
      </div>

      {/* Settings Options Card */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
        {/* Theme Settings */}
        <div className="space-y-3 pb-6 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Monitor className="w-4 h-4 text-indigo-400" />
            <span>Interface Theme Appearance</span>
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-2xl border flex items-center space-x-3 transition-all ${
                theme === 'dark'
                  ? 'bg-indigo-600/20 border-indigo-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Moon className="w-5 h-5 text-indigo-400" />
              <div className="text-left">
                <p className="text-xs font-bold">Dark Studio Mode</p>
                <p className="text-[10px] text-slate-400">High-contrast dark UI (Default)</p>
              </div>
            </button>

            <button
              onClick={() => setTheme('light')}
              className={`p-4 rounded-2xl border flex items-center space-x-3 transition-all ${
                theme === 'light'
                  ? 'bg-indigo-600/20 border-indigo-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sun className="w-5 h-5 text-amber-400" />
              <div className="text-left">
                <p className="text-xs font-bold">Light Clean Mode</p>
                <p className="text-[10px] text-slate-400">Bright daylight theme</p>
              </div>
            </button>
          </div>
        </div>

        {/* Processing Resolution */}
        <div className="space-y-3 pb-6 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Default Boundary Detection Resolution</span>
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {[
              { val: 600, label: 'Fast (600px)', desc: 'Mobile Low Spec' },
              { val: 800, label: 'Standard (800px)', desc: 'Balanced Speed & Detail' },
              { val: 1200, label: 'Ultra (1200px)', desc: 'Maximum Quad Precision' },
            ].map((item) => (
              <button
                key={item.val}
                onClick={() => setDefaultResolution(item.val)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  defaultResolution === item.val
                    ? 'bg-indigo-600/20 border-indigo-500 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <p className="text-xs font-bold">{item.label}</p>
                <p className="text-[10px] text-slate-400">{item.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* PDF Page Sizing Preferences */}
        <div className="space-y-3 pb-6 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Default PDF Document Page Format</span>
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'A4', label: 'ISO A4 (210 x 297 mm)', desc: 'International Standard' },
              { id: 'LETTER', label: 'US Letter (8.5 x 11 in)', desc: 'North America Standard' },
              { id: 'AUTO', label: 'Auto Aspect Ratio', desc: 'Preserves Original Photo Ratio' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setDefaultPdfFormat(item.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  defaultPdfFormat === item.id
                    ? 'bg-indigo-600/20 border-indigo-500 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <p className="text-xs font-bold">{item.label}</p>
                <p className="text-[10px] text-slate-400">{item.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleSave}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs px-6 py-3 rounded-xl shadow-lg shadow-indigo-500/25 transition-all active:scale-95"
          >
            Save Studio Settings
          </button>
        </div>
      </div>
    </div>
  );
};
