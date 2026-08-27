import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AdminStats, Internship } from '../types';
import {
  ShieldAlert,
  Database,
  RefreshCw,
  Plus,
  Trash2,
  Users,
  Briefcase,
  Layers,
  Sparkles,
  Search,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [internships, setInternships] = useState<Internship[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [searchFilter, setSearchFilter] = useState('');

  const fetchAdminData = async () => {
    try {
      setIsLoading(true);
      const [statsData, jobsData] = await Promise.all([
        api.admin.getStats(),
        api.admin.listInternships({ limit: 50 })
      ]);
      setStats(statsData);
      setInternships(jobsData);
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Failed to load admin telemetry' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleTriggerIngestion = async () => {
    try {
      setIsIngesting(true);
      setFeedbackMsg(null);
      const res = await api.admin.triggerIngestion({ limit: 1000, refresh_vectors: true });
      setFeedbackMsg({
        type: 'success',
        text: `Ingestion completed: ${res.inserted_count} new records added, ${res.duplicates_skipped} duplicates filtered.`
      });
      await fetchAdminData();
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Ingestion failed' });
    } finally {
      setIsIngesting(false);
    }
  };

  const handleReindexRAG = async () => {
    try {
      setIsReindexing(true);
      setFeedbackMsg(null);
      const res = await api.admin.reindexRAG();
      setFeedbackMsg({
        type: 'success',
        text: `Hybrid RAG successfully rebuilt across ${res.indexed_documents} active opportunities.`
      });
      await fetchAdminData();
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message || 'RAG re-indexing failed' });
    } finally {
      setIsReindexing(false);
    }
  };

  const handleDeleteJob = async (id: number) => {
    if (!window.confirm(`Are you sure you want to delete Internship #${id}?`)) return;
    try {
      await api.admin.deleteInternship(id);
      setFeedbackMsg({ type: 'success', text: `Internship #${id} successfully removed.` });
      setInternships((prev) => prev.filter((j) => j.id !== id));
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.message || 'Delete failed' });
    }
  };

  const filteredJobs = internships.filter(
    (j) =>
      j.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      j.company.toLowerCase().includes(searchFilter.toLowerCase()) ||
      j.domain.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Administrator Operations Portal
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">System Governance & Telemetry</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage data ingestion feeds, monitor Hybrid RAG indices, and audit verified internship listings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleReindexRAG}
            disabled={isReindexing}
            className="px-4 py-2.5 rounded-xl border border-border bg-card hover:bg-accent/10 text-sm font-semibold flex items-center gap-2 transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isReindexing ? 'animate-spin text-primary' : ''}`} />
            {isReindexing ? 'Reindexing RAG...' : 'Reindex Vectors'}
          </button>
          <button
            onClick={handleTriggerIngestion}
            disabled={isIngesting}
            className="px-4 py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 text-sm font-semibold flex items-center gap-2 transition-all shadow-md shadow-primary/20 disabled:opacity-50"
          >
            <Database className={`w-4 h-4 ${isIngesting ? 'animate-pulse' : ''}`} />
            {isIngesting ? 'Running Ingestion...' : 'Trigger Ingestion'}
          </button>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedbackMsg && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 ${
            feedbackMsg.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
              : 'bg-destructive/10 border-destructive/30 text-destructive'
          }`}
        >
          {feedbackMsg.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 shrink-0" />
          )}
          <span className="text-sm font-medium">{feedbackMsg.text}</span>
        </div>
      )}

      {/* Metric Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm">
            <div className="flex items-center justify-between text-muted-foreground mb-2">
              <span className="text-xs font-semibold uppercase">Total Users</span>
              <Users className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-black text-foreground">{stats.total_users}</div>
            <div className="text-xs text-muted-foreground mt-1">{stats.total_students} Students Registered</div>
          </div>

          <div className="p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm">
            <div className="flex items-center justify-between text-muted-foreground mb-2">
              <span className="text-xs font-semibold uppercase">Internships</span>
              <Briefcase className="w-4 h-4 text-accent" />
            </div>
            <div className="text-2xl font-black text-foreground">{stats.total_internships}</div>
            <div className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1">
              {stats.active_internships} Active Opportunities
            </div>
          </div>

          <div className="p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm">
            <div className="flex items-center justify-between text-muted-foreground mb-2">
              <span className="text-xs font-semibold uppercase">RAG Documents</span>
              <Layers className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-black text-foreground">{stats.rag_indexed_count}</div>
            <div className="text-xs text-muted-foreground mt-1">Dense + BM25 Indexed</div>
          </div>

          <div className="p-5 rounded-2xl border border-border bg-card/60 backdrop-blur-sm">
            <div className="flex items-center justify-between text-muted-foreground mb-2">
              <span className="text-xs font-semibold uppercase">Platform Engine</span>
              <Sparkles className="w-4 h-4 text-accent" />
            </div>
            <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 capitalize">
              {stats.ai_status}
            </div>
            <div className="text-xs text-muted-foreground mt-1">{stats.total_applications} Active Applications</div>
          </div>
        </div>
      )}

      {/* Internships Management Table */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-sm overflow-hidden shadow-sm">
        <div className="p-5 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-lg text-foreground">Verified Internship Directory</h3>
            <p className="text-xs text-muted-foreground">Showing active and curated opportunities in the database</p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search title, company, domain..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase border-b border-border/40">
              <tr>
                <th className="px-5 py-3.5">Company & Role</th>
                <th className="px-5 py-3.5">Domain</th>
                <th className="px-5 py-3.5">Location & Mode</th>
                <th className="px-5 py-3.5">Stipend</th>
                <th className="px-5 py-3.5">Source</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {filteredJobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-muted-foreground">
                    No matching internships found.
                  </td>
                </tr>
              ) : (
                filteredJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        {job.company_logo_url ? (
                          <img src={job.company_logo_url} alt="" className="w-8 h-8 object-contain rounded-md shrink-0 bg-muted/40 p-1" />
                        ) : (
                          <div className="w-8 h-8 rounded-md bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0">
                            {job.company[0]}
                          </div>
                        )}
                        <div>
                          <div className="font-semibold text-foreground">{job.title}</div>
                          <div className="text-xs text-muted-foreground">{job.company}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                        {job.domain}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">
                      <div>{job.location}</div>
                      <div className="font-medium text-foreground">{job.work_mode}</div>
                    </td>
                    <td className="px-5 py-4 text-xs font-medium text-foreground">{job.stipend || 'Competitive'}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">
                      <span className="px-2 py-0.5 rounded border border-border/80 bg-background text-[11px]">
                        {job.source_type || 'CURATED'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={() => handleDeleteJob(job.id)}
                        className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                        title="Delete Internship"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
