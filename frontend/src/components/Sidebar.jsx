import React from 'react';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 p-4 hidden md:flex flex-col space-y-2">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
        Navigation
      </div>
      <a href="#dashboard" className="px-3 py-2 rounded-lg bg-blue-600/10 text-blue-400 font-medium text-sm transition-all">
        Control Center
      </a>
      <a href="#evals" className="px-3 py-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 font-medium text-sm transition-all">
        LLM Evaluations
      </a>
      <a href="#monitoring" className="px-3 py-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 font-medium text-sm transition-all">
        App Monitoring
      </a>
    </aside>
  );
}