import React from 'react';
import AgentStatus from '../components/AgentStatus';
import ResultCard from '../components/ResultCard';

export default function Dashboard({ result, loading, onSubmit, logs, setLogs, repoContext, setRepoContext }) {
  return (
    <div className="space-y-6">
      <AgentStatus />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-base font-semibold text-blue-400 mb-4 uppercase tracking-wider">
            Submit Error Logs
          </h2>
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Application Logs / Traceback
              </label>
              <textarea
                rows="8"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                placeholder="Paste logs here..."
                value={logs}
                onChange={(e) => setLogs(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Repository Context (Optional)
              </label>
              <input
                type="text"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                placeholder="e.g., Python FastAPI with PostgreSQL"
                value={repoContext}
                onChange={(e) => setRepoContext(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 text-sm"
            >
              {loading ? 'Running Multi-Agent Pipeline...' : 'Run AI Debug & Fix Pipeline'}
            </button>
          </form>
        </div>

        <ResultCard
          title="Fix Synthesis & Recommendation"
          content={result ? result.fix_suggestion : null}
          status={result ? result.approval_status : 'Pending'}
        />
      </div>
    </div>
  );
}