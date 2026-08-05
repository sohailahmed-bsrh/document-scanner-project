import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FileText,
  LayoutDashboard,
  Scan,
  History,
  Settings,
  HelpCircle,
  Info,
  Sparkles,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/scanner', label: 'Scanner', icon: Scan },
    { path: '/history', label: 'History', icon: History },
    { path: '/settings', label: 'Settings', icon: Settings },
    { path: '/about', label: 'About', icon: Info },
    { path: '/help', label: 'Help', icon: HelpCircle },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-200">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                Devsil Scanner Pro
              </span>
              <span className="bg-indigo-500/10 text-indigo-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-500/20">
                PRO STUDIO
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              CamScanner & Adobe Scan Grade Suite
            </p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800/80">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-500/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="flex items-center space-x-3">
          <Link
            to="/scanner"
            className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg shadow-indigo-500/20 transition-all duration-200 active:scale-95"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Scan</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
