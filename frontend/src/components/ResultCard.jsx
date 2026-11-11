import React from 'react';

export default function ResultCard({ title, content, status }) {
  return (
    <div className="bg-slate-800/50 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col h-full">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-indigo-300 uppercase tracking-wider">{title}</h3>
        {status && (
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase">
            {status}
          </span>
        )}
      </div>
      <div className="flex-1 bg-slate-900 border border-slate-700/60 rounded-lg p-4 font-mono text-xs text-slate-300 overflow-y-auto max-h-[350px] whitespace-pre-wrap">
        {content || 'Awaiting execution data...'}
      </div>
    </div>
  );
}