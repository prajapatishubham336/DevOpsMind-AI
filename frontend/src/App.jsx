
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import AgentStatus from './components/AgentStatus';
import ResultCard from './components/ResultCard';
import { runLogAnalysis } from './services/api';

export default function App() {
  const [logs, setLogs] = useState('');
  const [repoContext, setRepoContext] = useState('');

  const [githubOwner, setGithubOwner] = useState('');
  const [githubRepo, setGithubRepo] = useState('');
  const [appId, setAppId] = useState('');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();

    if (!logs.trim()) {
      alert('Please enter application logs.');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const data = await runLogAnalysis(
        logs,
        repoContext,
        githubOwner,
        githubRepo,
        appId
      );

      console.log('Multi-Agent API Response:', data);

      setResult(data);

    } catch (err) {
      console.error(
        'Pipeline Error:',
        err.response?.data || err.message
      );

      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        'Unknown backend error';

      alert(`Pipeline Failed: ${errorMessage}`);

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">

      <Navbar />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">

        {/* Agent Status Bar */}
        <AgentStatus />

        {/* Control Panel Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Input Form */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">

            <h2 className="text-base font-semibold text-blue-400 mb-4 uppercase tracking-wider">
              Submit Error Logs
            </h2>

            <form onSubmit={handleAnalyze} className="space-y-4">

              {/* Application Logs */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Application Logs / Traceback
                </label>

                <textarea
                  rows="8"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                  placeholder="Paste logs here (e.g., ConnectionRefusedError...)"
                  value={logs}
                  onChange={(e) => setLogs(e.target.value)}
                  required
                />
              </div>

              {/* Repository Context */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Repository Context (Optional)
                </label>

                <input
                  type="text"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                  placeholder="e.g., Python FastAPI with PostgreSQL backend"
                  value={repoContext}
                  onChange={(e) => setRepoContext(e.target.value)}
                />
              </div>

              {/* GitHub Owner */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  GitHub Owner (Optional)
                </label>

                <input
                  type="text"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                  placeholder="Your GitHub username or organization"
                  value={githubOwner}
                  onChange={(e) => setGithubOwner(e.target.value)}
                />
              </div>

              {/* GitHub Repository */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  GitHub Repository (Optional)
                </label>

                <input
                  type="text"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                  placeholder="Your repository name"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                />
              </div>

              {/* Application ID */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Registered Application ID (Optional)
                </label>

                <input
                  type="number"
                  min="1"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-200"
                  placeholder="Enter registered Application ID"
                  value={appId}
                  onChange={(e) => setAppId(e.target.value)}
                />
              </div>

              {/* Run Pipeline Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 text-sm"
              >
                {loading
                  ? 'Running Multi-Agent Pipeline...'
                  : 'Run AI Debug & Fix Pipeline'}
              </button>

            </form>
          </div>

          {/* Results Display */}
          <div className="grid grid-cols-1 gap-6">

            <ResultCard
              title="Fix Synthesis & Recommendation"
              content={
                result
                  ? result.fix_suggestion || 'No fix suggestion returned.'
                  : null
              }
              status={
                result
                  ? result.approval_status || result.status || 'Completed'
                  : 'Pending'
              }
            />

            {result && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

                <h3 className="text-sm font-semibold text-blue-400 mb-3">
                  Multi-Agent Execution Results
                </h3>

                <p className="text-xs text-slate-300 mb-3">
                  <strong>Active Agents:</strong>
                </p>

                <pre className="text-xs text-emerald-400 whitespace-pre-wrap break-words">
                  {JSON.stringify(result.active_agents || [], null, 2)}
                </pre>

                <div className="border-t border-slate-800 my-4" />

                <p className="text-xs text-slate-300 mb-2">
                  <strong>Manager Plan</strong>
                </p>

                <pre className="text-xs text-slate-400 whitespace-pre-wrap break-words">
                  {JSON.stringify(result.manager_plan || 'Not provided', null, 2)}
                </pre>

                <div className="border-t border-slate-800 my-4" />

                <p className="text-xs text-slate-300 mb-2">
                  <strong>Log Analysis</strong>
                </p>

                <pre className="text-xs text-slate-400 whitespace-pre-wrap break-words">
                  {JSON.stringify(result.log_analysis || 'Not executed', null, 2)}
                </pre>

                <div className="border-t border-slate-800 my-4" />

                <p className="text-xs text-slate-300 mb-2">
                  <strong>GitHub Analysis</strong>
                </p>

                <pre className="text-xs text-slate-400 whitespace-pre-wrap break-words">
                  {JSON.stringify(result.github_analysis || 'Not executed', null, 2)}
                </pre>

                <div className="border-t border-slate-800 my-4" />

                <p className="text-xs text-slate-300 mb-2">
                  <strong>Monitoring Analysis</strong>
                </p>

                <pre className="text-xs text-slate-400 whitespace-pre-wrap break-words">
                  {JSON.stringify(result.monitoring_analysis || 'Not executed', null, 2)}
                </pre>

              </div>
            )}

          </div>
        </div>

        {/* Self-Healing Safety Gate */}
        {result && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex justify-between items-center shadow-xl">

            <div>
              <h4 className="text-sm font-semibold text-emerald-400">
                Self-Healing Safety Gate
              </h4>

              <p className="text-xs text-slate-400">
                Review recommendations before authorizing deployment.
              </p>
            </div>

            <button
              onClick={() =>
                alert('Fix proposal approved securely! Ready for deployment.')
              }
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition-all shadow-lg shadow-emerald-600/20"
            >
              Approve & Deploy Fix
            </button>

          </div>
        )}

      </main>
    </div>
  );
}
