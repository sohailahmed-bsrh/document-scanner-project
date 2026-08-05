import React, { useEffect, useState } from 'react';
import {
  History,
  Trash2,
  FileText,
  Download,
  Search,
  Grid,
  List,
  CheckSquare,
  Square,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';
import { ScanHistoryRecord } from '../types/scanner';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<ScanHistoryRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewType, setViewType] = useState<'grid' | 'list'>('grid');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [exportingPdf, setExportingPdf] = useState<boolean>(false);
  const [previewFilename, setPreviewFilename] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory();
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch scan history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (filename: string) => {
    if (!confirm('Are you sure you want to delete this scan?')) return;
    try {
      await api.deleteHistoryItem(filename);
      setHistory(history.filter((h) => h.filename !== filename));
      setSelectedIds(selectedIds.filter((id) => id !== filename));
    } catch (err) {
      alert('Failed to delete item.');
    }
  };

  const toggleSelect = (filename: string) => {
    if (selectedIds.includes(filename)) {
      setSelectedIds(selectedIds.filter((id) => id !== filename));
    } else {
      setSelectedIds([...selectedIds, filename]);
    }
  };

  const handleExportSelectedPdf = async () => {
    if (selectedIds.length === 0) return;
    setExportingPdf(true);
    try {
      const res = await api.exportPdf(selectedIds, 'multi_page_scan.pdf', 'A4');
      window.open(res.download_url, '_blank');
    } catch (err) {
      alert('Multi-page PDF export failed.');
    } finally {
      setExportingPdf(false);
    }
  };

  const filteredHistory = history.filter(
    (item) =>
      item.original_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.mode.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center space-x-2">
            <History className="w-6 h-6 text-indigo-400" />
            <span>Document Scan Library ({history.length})</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage saved scans, preview high-res outputs, and batch export multi-page PDF documents.
          </p>
        </div>

        {selectedIds.length > 0 && (
          <button
            onClick={handleExportSelectedPdf}
            disabled={exportingPdf}
            className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs px-5 py-3 rounded-xl shadow-lg shadow-indigo-500/25 transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>Export Selected ({selectedIds.length}) to Multi-Page PDF</span>
          </button>
        )}
      </div>

      {/* Toolbar & Filter Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-slate-800">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by file name or filter..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto justify-between md:justify-end">
          <button
            onClick={() =>
              setSelectedIds(
                selectedIds.length === history.length ? [] : history.map((h) => h.filename)
              )
            }
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
          >
            {selectedIds.length === history.length ? 'Deselect All' : 'Select All'}
          </button>

          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setViewType('grid')}
              className={`p-1.5 rounded-lg transition-colors ${
                viewType === 'grid' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Grid View"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewType('list')}
              className={`p-1.5 rounded-lg transition-colors ${
                viewType === 'list' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Scan Items Display */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 animate-pulse text-sm">
          Loading library scans...
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="glass-panel p-12 rounded-3xl text-center space-y-3 border border-slate-800">
          <History className="w-12 h-12 text-slate-600 mx-auto" />
          <p className="text-sm font-bold text-slate-300">No matching scans found</p>
          <p className="text-xs text-slate-500">Try adjusting your search query or process a new scan.</p>
        </div>
      ) : viewType === 'grid' ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredHistory.map((item) => {
            const isSelected = selectedIds.includes(item.filename);

            return (
              <div
                key={item.id}
                className={`group relative rounded-2xl bg-slate-900 border transition-all duration-200 overflow-hidden ${
                  isSelected ? 'border-indigo-500 ring-2 ring-indigo-500/30' : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Select Checkbox Overlay */}
                <button
                  onClick={() => toggleSelect(item.filename)}
                  className="absolute top-3 left-3 z-10 p-1 rounded-lg bg-slate-900/80 text-white backdrop-blur-md"
                >
                  {isSelected ? (
                    <CheckSquare className="w-4 h-4 text-indigo-400" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-400" />
                  )}
                </button>

                {/* Image Aspect Preview */}
                <div
                  onClick={() => setPreviewFilename(item.filename)}
                  className="aspect-[3/4] bg-slate-950 overflow-hidden relative cursor-pointer"
                >
                  <img
                    src={`/api/scans/file/${item.filename}`}
                    alt={item.original_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                {/* Card Details */}
                <div className="p-3 space-y-2">
                  <p className="text-xs font-bold text-slate-200 truncate" title={item.original_name}>
                    {item.original_name}
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="capitalize px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {item.mode.replace('_', ' ')}
                    </span>
                    <span>{item.width}x{item.height}</span>
                  </div>

                  <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
                    <a
                      href={`/api/scans/file/${item.filename}`}
                      download={item.filename}
                      className="text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
                    >
                      <Download className="w-3 h-3" />
                      <span>Download</span>
                    </a>

                    <button
                      onClick={() => handleDelete(item.filename)}
                      className="text-slate-500 hover:text-red-400 p-1 transition-colors"
                      title="Delete scan"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* List View */
        <div className="glass-panel rounded-3xl border border-slate-800 divide-y divide-slate-800/80 overflow-hidden">
          {filteredHistory.map((item) => {
            const isSelected = selectedIds.includes(item.filename);

            return (
              <div
                key={item.id}
                className="p-4 flex items-center justify-between hover:bg-slate-900/60 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <button onClick={() => toggleSelect(item.filename)}>
                    {isSelected ? (
                      <CheckSquare className="w-4 h-4 text-indigo-400" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400" />
                    )}
                  </button>

                  <div
                    onClick={() => setPreviewFilename(item.filename)}
                    className="w-12 h-16 rounded-lg bg-slate-950 overflow-hidden border border-slate-800 cursor-pointer flex-shrink-0"
                  >
                    <img
                      src={`/api/scans/file/${item.filename}`}
                      alt={item.original_name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div>
                    <p className="text-sm font-bold text-white">{item.original_name}</p>
                    <p className="text-xs text-slate-400 capitalize">
                      Filter: {item.mode.replace('_', ' ')} • Dimensions: {item.width} x {item.height} px
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <a
                    href={`/api/scans/file/${item.filename}`}
                    download={item.filename}
                    className="p-2 rounded-xl bg-slate-900 hover:bg-indigo-600 text-slate-300 hover:text-white transition-colors"
                    title="Download Scan"
                  >
                    <Download className="w-4 h-4" />
                  </a>

                  <button
                    onClick={() => handleDelete(item.filename)}
                    className="p-2 rounded-xl bg-slate-900 hover:bg-red-600/20 text-slate-400 hover:text-red-400 transition-colors"
                    title="Delete Scan"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Fullscreen Preview Modal */}
      {previewFilename && (
        <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="relative max-w-4xl w-full glass-panel p-4 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">{previewFilename}</h3>
              <button
                onClick={() => setPreviewFilename(null)}
                className="text-xs font-bold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700"
              >
                Close ✕
              </button>
            </div>

            <div className="max-h-[70vh] overflow-auto flex items-center justify-center bg-slate-950 rounded-2xl p-2">
              <img
                src={`/api/scans/file/${previewFilename}`}
                alt="Full Preview"
                className="max-h-[65vh] w-auto object-contain rounded-xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
