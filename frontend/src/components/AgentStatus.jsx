import React from 'react';

export default function AgentStatus({ activeAgents = [] }) {
  const agents = [
    { id: 'manager', name: 'Manager Agent' },
    { id: 'log_agent', name: 'Log Analysis Agent' },
    { id: 'github_agent', name: 'GitHub Intelligence Agent' },
    { id: 'monitoring_agent', name: 'Monitoring Agent' },
    { id: 'fix_agent', name: 'Fix & Synthesis Agent' },
  ];

  return (
    <div className="bg-slate-800/50 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">AI Agents Pipeline</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-slate-900 border border-slate-700/60 rounded-lg p-3 text-center">
            <span className="block text-xs font-medium text-slate-400 mb-1">{agent.name}</span>
            <span className="inline-block px-2 py-0.5 text-[10px] font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Ready / Active
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}