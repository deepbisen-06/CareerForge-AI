import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Kanban as KanbanIcon, Plus, Clock, ExternalLink, Trash2, Edit3,
  CheckCircle2, AlertCircle, Sparkles, ChevronRight, Loader2, ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { Application, ApplicationStatus } from '../types';

const COLUMNS: { id: ApplicationStatus; name: string; color: string }[] = [
  { id: 'SAVED', name: 'Saved', color: 'border-blue-500/40 text-blue-500' },
  { id: 'APPLIED', name: 'Applied', color: 'border-indigo-500/40 text-indigo-500' },
  { id: 'ASSESSMENT', name: 'Assessment', color: 'border-amber-500/40 text-amber-500' },
  { id: 'INTERVIEW', name: 'Interview', color: 'border-purple-500/40 text-purple-500' },
  { id: 'OFFER', name: 'Offer', color: 'border-emerald-500/40 text-emerald-500' },
  { id: 'REJECTED', name: 'Archived', color: 'border-muted text-muted-foreground' }
];

export const ApplicationTracker: React.FC = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchApps = () => {
    setIsLoading(true);
    api.applications.list()
      .then(setApplications)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchApps();
  }, []);

  const handleStatusChange = async (appId: number, newStatus: ApplicationStatus) => {
    try {
      await api.applications.update(appId, { status: newStatus });
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, status: newStatus } : a));
    } catch (err) {
      console.error("Error updating status:", err);
    }
  };

  const handleDelete = async (appId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.applications.delete(appId);
      setApplications(prev => prev.filter(a => a.id !== appId));
    } catch (err) {
      console.error("Error deleting application:", err);
    }
  };

  const getDeadlineBadge = (deadlineStatus?: string, deadline?: string) => {
    if (!deadline) return null;
    if (deadlineStatus === 'Overdue') {
      return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 border border-rose-500/20">Overdue ({deadline})</span>;
    }
    if (deadlineStatus === 'Urgent') {
      return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">Urgent ({deadline})</span>;
    }
    return <span className="text-[11px] text-muted-foreground">{deadline}</span>;
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <KanbanIcon className="w-3.5 h-3.5" /> Multi-Stage Pipeline Tracker
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Application Tracker Kanban</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Track applications from bookmark to offer with automated deadline alerts and match scores.
          </p>
        </div>

        <button
          onClick={() => navigate('/internships')}
          className="px-4 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition shadow-md shadow-primary/20 flex items-center gap-1.5 self-start"
        >
          <Plus className="w-4 h-4" /> Add from Explorer
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Loading tracked applications...</p>
        </div>
      ) : (
        /* Kanban Columns Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 overflow-x-auto pb-4">
          {COLUMNS.map(col => {
            const colApps = applications.filter(a => a.status === col.id);
            return (
              <div key={col.id} className="flex flex-col min-w-[240px] rounded-2xl bg-card/50 border border-border p-3 space-y-3">
                {/* Column Header */}
                <div className={`flex items-center justify-between pb-2 border-b-2 ${col.color}`}>
                  <span className="font-bold text-xs uppercase tracking-wider">{col.name}</span>
                  <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center text-[10px] font-bold text-foreground">
                    {colApps.length}
                  </span>
                </div>

                {/* Cards Container */}
                <div className="flex-1 space-y-3 min-h-[300px]">
                  {colApps.map(app => (
                    <div
                      key={app.id}
                      onClick={() => navigate(`/internships/${app.internship_id}`)}
                      className="p-3.5 rounded-2xl bg-card border border-border/80 hover:border-primary/40 hover:shadow-md transition cursor-pointer space-y-2 group relative"
                    >
                      <div className="flex items-start justify-between gap-1">
                        <div>
                          <span className="text-[10px] font-bold text-primary px-2 py-0.5 rounded-full bg-primary/10">
                            {app.internship.company}
                          </span>
                          <h4 className="font-bold text-xs mt-1 text-foreground line-clamp-1 group-hover:text-primary transition">
                            {app.internship.title}
                          </h4>
                        </div>
                        <button
                          onClick={(e) => handleDelete(app.id, e)}
                          className="text-muted-foreground hover:text-destructive p-1 rounded transition opacity-0 group-hover:opacity-100"
                          title="Delete card"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {/* Match Score & Deadline */}
                      <div className="flex items-center justify-between text-[11px] pt-1">
                        <span className="font-extrabold text-emerald-600 dark:text-emerald-400">
                          {app.match_score || 85}% Match
                        </span>
                        {getDeadlineBadge(app.deadline_status, app.deadline)}
                      </div>

                      {/* Move Stage Selector */}
                      <div className="pt-2 border-t border-border/60">
                        <select
                          value={app.status}
                          onClick={(e) => e.stopPropagation()}
                          onChange={(e) => handleStatusChange(app.id, e.target.value as ApplicationStatus)}
                          className="w-full bg-muted/40 border border-border rounded-lg text-[10px] font-semibold p-1 text-muted-foreground focus:outline-none"
                        >
                          {COLUMNS.map(c => (
                            <option key={c.id} value={c.id}>Move to: {c.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ApplicationTracker;
