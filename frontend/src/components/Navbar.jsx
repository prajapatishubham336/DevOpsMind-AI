import React from 'react';

export default function Navbar() {
  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center">
      <div className="flex items-center space-x-3">
        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          DevOpsMind AI
        </span>
        <span className="text-xs bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-full border border-blue-500/20 font-medium">
          Multi-Agent v2.0
        </span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span className="text-sm text-slate-300 font-medium">System Online</span>
      </div>
    </header>
  );
}