import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Scan,
  History,
  FileCheck,
  Zap,
  Sparkles,
  ArrowRight,
  Download,
  FileText,
  Sliders,
  Shield,
  Layers,
  FileCode,
} from 'lucide-react';
import { api } from '../services/api';
import { ScanHistoryRecord } from '../types/scanner';

export const DashboardPage: React.FC = () => {
  const [history, setHistory] = useState<ScanHistoryRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [samples, setSamples] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [histData, sampleData] = await Promise.all([
          api.getHistory().catch(() => []),
          api.getSampleImages().catch(() => ({ samples: [] })),
        ]);
        setHistory(histData);
        setSamples(sampleData.samples || []);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Banner Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/80 to-slate-900 border border-slate-800 p-8 md:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/3 -mb-12 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Commercial Document Processing Engine v2.0</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            CamScanner & Adobe Scan Grade{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-indigo-200 bg-clip-text text-transparent">
              Document Studio
            </span>
          </h1>

          <p className="text-slate-300 text-base md:text-lg font-normal leading-relaxed">
            Transform photos into crystal-clear, professional PDF documents. Automated paper corner detection, illumination whitening, interactive perspective correction, and high-performance multi-page PDF generation.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              to="/scanner"
              className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-sm px-6 py-3.5 rounded-2xl shadow-xl shadow-indigo-500/25 transition-all duration-200 active:scale-95"
            >
              <Scan className="w-5 h-5" />
              <span>Launch Studio Scanner</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/history"
              className="flex items-center space-x-2 bg-slate-800/80 hover:bg-slate-800 text-slate-200 font-semibold text-sm px-6 py-3.5 rounded-2xl border border-slate-700 transition-all duration-200"
            >
              <History className="w-5 h-5 text-indigo-400" />
              <span>View Document Library ({history.length})</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Metrics Grid */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-6 rounded-2xl border border-slate-800/80 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{history.length}</p>
            <p className="text-xs text-slate-400 font-medium">Scanned Documents</p>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800/80 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">4-Tier</p>
            <p className="text-xs text-slate-400 font-medium">Quad Detector Engine</p>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800/80 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center border border-teal-500/20">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">9 Presets</p>
            <p className="text-xs text-slate-400 font-medium">Filter Enhancement Suite</p>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800/80 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">100%</p>
            <p className="text-xs text-slate-400 font-medium">On-Device Data Security</p>
          </div>
        </div>
      </section>

      {/* Feature Modules Overview */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <span>Professional Features</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
              <Sliders className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">CamScanner Magic Color 2.0</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Illumination morphology division transforms shadowed, yellowish smartphone photos into pristine 100% white paper scans while preserving original text color stamps.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center">
              <Scan className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Interactive Quad Crop</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Drag-and-drop 4 corner handles directly on the high-res canvas with automatic paper perimeter snapping and fine-grain coordinate control.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl bg-teal-600/20 text-teal-400 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Multi-Page PDF Suite</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Combine multiple scans into a single multi-page PDF with standardized page sizing (A4, Letter, Auto) and high resolution export.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Scans Feed */}
      <section className="glass-panel p-6 rounded-3xl space-y-4 border border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <History className="w-5 h-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white">Recent Document Scans</h2>
          </div>
          <Link to="/history" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300">
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 text-sm animate-pulse">
            Loading recent scan history...
          </div>
        ) : history.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <FileCode className="w-12 h-12 text-slate-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">No scanned documents yet</p>
            <p className="text-xs text-slate-500">
              Upload or scan your first document to build your library.
            </p>
            <Link
              to="/scanner"
              className="inline-flex items-center space-x-2 bg-indigo-600 text-white text-xs font-bold px-4 py-2 rounded-xl"
            >
              <Scan className="w-4 h-4" />
              <span>Start First Scan</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {history.slice(0, 6).map((item) => (
              <div
                key={item.id}
                className="group relative rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden hover:border-indigo-500/50 transition-all duration-200"
              >
                <div className="aspect-[3/4] overflow-hidden bg-slate-950 relative">
                  <img
                    src={`/api/scans/file/${item.filename}`}
                    alt={item.original_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-60"></div>
                </div>

                <div className="p-3 space-y-1">
                  <p className="text-xs font-bold text-slate-200 truncate" title={item.original_name}>
                    {item.original_name}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="capitalize">{item.mode.replace('_', ' ')}</span>
                    <span>{item.width}x{item.height}</span>
                  </div>
                </div>

                <a
                  href={`/api/scans/file/${item.filename}`}
                  download={item.filename}
                  className="absolute top-2 right-2 p-1.5 rounded-lg bg-slate-900/80 text-slate-200 opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-indigo-600 hover:text-white"
                  title="Download File"
                >
                  <Download className="w-3.5 h-3.5" />
                </a>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
