import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Play, CheckCircle2, AlertCircle, Clock, ChevronRight, XCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { AgentRun } from '../types';

export const AgentRunsHistory: React.FC = () => {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.agent.listRuns(50)
      .then(setRuns)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3 h-3" /> Completed</span>;
      case 'AWAITING_APPROVAL':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"><AlertCircle className="w-3 h-3" /> Awaiting Approval</span>;
      case 'RUNNING':
      case 'PLANNING':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20 animate-pulse"><RefreshCw className="w-3 h-3 animate-spin" /> {status}</span>;
      case 'FAILED':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"><XCircle className="w-3 h-3" /> Failed</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-muted text-muted-foreground">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-foreground flex items-center gap-2.5">
            <Cpu className="w-6 h-6 text-primary" />
            <span>Agent Run History</span>
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Audit trail of autonomous executions, plans, tool invocations, and synthesized reports.
          </p>
        </div>
        <button
          onClick={() => navigate('/workspace')}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:opacity-90 transition flex items-center gap-1.5 shadow-sm shadow-primary/20 shrink-0"
        >
          <Play className="w-3.5 h-3.5" />
          <span>New Agent Run</span>
        </button>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-muted-foreground">Loading history...</div>
      ) : runs.length === 0 ? (
        <div className="p-12 text-center text-muted-foreground rounded-2xl bg-card border border-border">
          <p className="text-sm">No agent runs recorded yet.</p>
          <button
            onClick={() => navigate('/workspace')}
            className="mt-4 px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground"
          >
            Launch First Goal
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run) => (
            <div
              key={run.id}
              onClick={() => navigate('/workspace')}
              className="p-5 rounded-2xl bg-card border border-border hover:border-primary/40 transition cursor-pointer shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 group"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black text-primary">Run #{run.id}</span>
                  {getStatusBadge(run.status)}
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(run.created_at).toLocaleDateString()} {new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-foreground line-clamp-1 group-hover:text-primary transition-colors">
                  "{run.goal}"
                </h3>
                <p className="text-xs text-muted-foreground">
                  {run.execution_plan?.length || 0} plan steps • {run.final_summary?.metrics?.total_evaluated || 0} opportunities evaluated
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                <span>View Results</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentRunsHistory;
