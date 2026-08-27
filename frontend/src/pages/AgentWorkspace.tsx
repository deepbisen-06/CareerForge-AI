import React, { useState, useEffect } from 'react';
import {
  Sparkles, Play, CheckCircle2, Circle, AlertCircle, Clock, ArrowRight,
  ShieldCheck, FileText, Check, ExternalLink, RefreshCw, Send,
  Cpu, Target, ChevronRight, XCircle, AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';
import { AgentRun, AgentEvent } from '../types';

const SUGGESTED_GOALS = [
  "Find AI/ML internships matching my profile, prioritize remote opportunities, verify eligibility, and prepare me to apply.",
  "Analyze the internships I already saved and tell me which ones I should apply to first.",
  "Identify critical skill gaps for Full Stack Web Developer internships and create a prep roadmap.",
  "Evaluate top matched Data Science internships and prepare my application package."
];

export const AgentWorkspace: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeRun, setActiveRun] = useState<AgentRun | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isApproving, setIsApproving] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'plan' | 'timeline' | 'opportunities' | 'package'>('overview');

  // Load latest run on mount
  useEffect(() => {
    api.agent.listRuns(1)
      .then((runs) => {
        if (runs && runs.length > 0) {
          setActiveRun(runs[0]);
          loadEvents(runs[0].id);
        }
      })
      .catch(() => {});
  }, []);

  const loadEvents = async (runId: number) => {
    try {
      const evs = await api.agent.getEvents(runId);
      setEvents(evs);
    } catch {
      // fallback
    }
  };

  const handleExecute = async (goalText?: string) => {
    const textToRun = goalText || goal;
    if (!textToRun.trim() || isExecuting) return;

    setIsExecuting(true);
    setError(null);
    try {
      const run = await api.agent.createRun(textToRun);
      setActiveRun(run);
      if (run.id) {
        await loadEvents(run.id);
      }
      setActiveTab('overview');
    } catch (err: any) {
      setError(err.message || 'Failed to execute agent workflow');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleApprove = async () => {
    if (!activeRun) return;
    setIsApproving(true);
    try {
      const updated = await api.agent.approveRun(activeRun.id, "Approved via CareerForge Workspace");
      setActiveRun(updated);
      await loadEvents(activeRun.id);
    } catch (err: any) {
      setError(err.message || 'Failed to approve application package');
    } finally {
      setIsApproving(false);
    }
  };

  const summary = activeRun?.final_summary;
  const topOpps = summary?.top_opportunities || [];
  const appPackage = summary?.application_package;

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3.5 h-3.5" /> Completed</span>;
      case 'AWAITING_APPROVAL':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 animate-pulse"><AlertCircle className="w-3.5 h-3.5" /> Awaiting Your Approval</span>;
      case 'RUNNING':
      case 'PLANNING':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20 animate-pulse"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> {status}</span>;
      case 'FAILED':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"><XCircle className="w-3.5 h-3.5" /> Failed</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-muted text-muted-foreground">Ready</span>;
    }
  };

  const getEligibilityBadge = (elStatus: string) => {
    switch (elStatus) {
      case 'ELIGIBLE':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">ELIGIBLE</span>;
      case 'PARTIALLY_ELIGIBLE':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30">PARTIAL</span>;
      case 'NOT_ELIGIBLE':
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30">NOT ELIGIBLE</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-500/15 text-slate-600 dark:text-slate-400 border border-slate-500/30">UNKNOWN</span>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Banner / Identity */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-card via-card to-primary/5 border border-border p-6 md:p-8 shadow-sm">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 mb-2.5">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground font-black text-xl shadow-md shadow-primary/20">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-black tracking-tight text-foreground">CareerForge AI</h1>
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-primary/10 text-primary border border-primary/20">
                    Taskmaster Agent
                  </span>
                </div>
                <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
                  <Sparkles className="w-3.5 h-3.5 text-accent" /> Powered by Google Gemini ADK & Deterministic Tool Matrix
                </p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground max-w-2xl leading-relaxed">
              Give CareerForge a high-level goal. The agent autonomously builds an execution plan, discovers verified opportunities, computes deterministic compatibility, verifies eligibility, analyzes skill gaps, prepares tailored materials, and requests your approval.
            </p>
          </div>

          {activeRun && (
            <div className="flex flex-col items-start md:items-end gap-2 shrink-0">
              <div className="text-xs text-muted-foreground">Current Run State</div>
              {getStatusBadge(activeRun.status)}
              <div className="text-[11px] text-muted-foreground">Run #{activeRun.id} • {new Date(activeRun.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
          )}
        </div>
      </div>

      {/* Goal Input & Suggested Goals */}
      <div className="rounded-2xl bg-card border border-border p-5 md:p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-foreground">
          <Target className="w-4 h-4 text-primary" />
          <span>What would you like CareerForge to accomplish?</span>
        </div>

        <div className="relative">
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g. Find AI/ML internships matching my profile, prioritize remote opportunities, verify eligibility, and prepare me to apply..."
            rows={3}
            className="w-full px-4 py-3 rounded-xl bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm resize-none"
            disabled={isExecuting}
          />
          <div className="flex items-center justify-between mt-3">
            <span className="text-[11px] text-muted-foreground">
              Autonomous multi-step execution loop with human-in-the-loop gate
            </span>
            <button
              onClick={() => handleExecute()}
              disabled={!goal.trim() || isExecuting}
              className="px-6 py-2.5 rounded-xl font-semibold text-sm bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 transition shadow-sm shadow-primary/30 flex items-center gap-2"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Agent Executing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Execute Agent</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Suggested Goals Chips */}
        <div className="space-y-2 pt-2 border-t border-border/60">
          <span className="text-xs font-semibold text-muted-foreground">Suggested High-Yield Goals:</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {SUGGESTED_GOALS.map((sGoal, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setGoal(sGoal);
                  handleExecute(sGoal);
                }}
                disabled={isExecuting}
                className="text-left p-2.5 rounded-xl bg-accent/40 hover:bg-accent/80 border border-border/80 text-xs text-foreground font-medium transition flex items-start gap-2 group"
              >
                <ChevronRight className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5 group-hover:translate-x-0.5 transition-transform" />
                <span className="leading-snug">{sGoal}</span>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Active Run Workspace Area */}
      {activeRun && (
        <div className="space-y-6">
          {/* Navigation Tabs for Run Results */}
          <div className="flex items-center gap-2 border-b border-border pb-2 overflow-x-auto">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'overview'
                  ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              }`}
            >
              Executive Summary
            </button>
            <button
              onClick={() => setActiveTab('plan')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'plan'
                  ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              }`}
            >
              <span>Execution Plan</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-background/30">{activeRun.execution_plan?.length || 0}</span>
            </button>
            <button
              onClick={() => setActiveTab('opportunities')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'opportunities'
                  ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              }`}
            >
              <span>Ranked Opportunities</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-background/30">{topOpps.length}</span>
            </button>
            {appPackage && (
              <button
                onClick={() => setActiveTab('package')}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
                  activeTab === 'package'
                    ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/20'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                }`}
              >
                <span>Application Draft</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-500 font-bold">Approval</span>
              </button>
            )}
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'timeline'
                  ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              }`}
            >
              <span>Live Activity Stream</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-background/30">{events.length}</span>
            </button>
          </div>

          {/* TAB 1: EXECUTIVE OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Human-in-the-Loop Approval Banner */}
              {activeRun.status === 'AWAITING_APPROVAL' && appPackage && (
                <div className="rounded-2xl bg-gradient-to-r from-amber-500/10 via-card to-amber-500/5 border border-amber-500/30 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5 text-amber-500" />
                      <h3 className="text-base font-bold text-foreground">Application Package Ready — Human Approval Required</h3>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      CareerForge prepared tailored materials for <strong>{appPackage.company} ({appPackage.title})</strong>. Grounded strictly in verified facts with anti-hallucination validation.
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <button
                      onClick={() => setActiveTab('package')}
                      className="px-4 py-2 rounded-xl text-xs font-semibold border border-border bg-card hover:bg-accent text-foreground transition"
                    >
                      Review Materials
                    </button>
                    <button
                      onClick={handleApprove}
                      disabled={isApproving}
                      className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-1.5 shadow-sm shadow-emerald-600/30"
                    >
                      {isApproving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                      <span>Approve & Finalize</span>
                    </button>
                  </div>
                </div>
              )}

              {/* High-Impact Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="rounded-2xl bg-card border border-border p-5 shadow-sm">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Evaluated Roles</span>
                  <div className="text-3xl font-black text-foreground mt-2">{summary?.metrics?.total_evaluated || topOpps.length || 0}</div>
                  <p className="text-[11px] text-muted-foreground mt-1">Verified via Hybrid RAG Engine</p>
                </div>
                <div className="rounded-2xl bg-card border border-border p-5 shadow-sm">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">High Match Fit (≥75%)</span>
                  <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-2">{summary?.metrics?.high_confidence_matches || topOpps.filter(o => o.match_score >= 75).length}</div>
                  <p className="text-[11px] text-muted-foreground mt-1">Multi-factor deterministic score</p>
                </div>
                <div className="rounded-2xl bg-card border border-border p-5 shadow-sm">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Verified Eligible</span>
                  <div className="text-3xl font-black text-primary mt-2">{summary?.metrics?.verified_eligible || topOpps.filter(o => o.eligibility_status === 'ELIGIBLE').length}</div>
                  <p className="text-[11px] text-muted-foreground mt-1">Education & batch verified</p>
                </div>
              </div>

              {/* Synthesis & Next Actions */}
              <div className="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary" />
                  <span>Agent Executive Summary</span>
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {summary?.executive_summary || "Agent analyzed your profile, executed RAG opportunity discovery, calculated deterministic match scores, and performed eligibility checks."}
                </p>

                {summary?.next_actions && summary.next_actions.length > 0 && (
                  <div className="pt-4 border-t border-border space-y-2">
                    <span className="text-xs font-bold text-foreground">Recommended Next Actions:</span>
                    <div className="space-y-1.5">
                      {summary.next_actions.map((act, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                          <span className="w-4 h-4 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            {i + 1}
                          </span>
                          <span>{act}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Top Matches Carousel/List */}
              {topOpps.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-foreground">Top Evaluated Opportunities</h3>
                    <button onClick={() => setActiveTab('opportunities')} className="text-xs text-primary hover:underline flex items-center gap-1">
                      View all ({topOpps.length}) <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {topOpps.slice(0, 2).map((opp) => (
                      <div key={opp.internship_id} className="rounded-2xl bg-card border border-border p-5 shadow-sm space-y-3 hover:border-primary/40 transition">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="font-bold text-sm text-foreground">{opp.title}</h4>
                            <p className="text-xs text-muted-foreground font-medium">{opp.company} • {opp.location} ({opp.work_mode})</p>
                          </div>
                          <div className="text-right shrink-0">
                            <div className="text-lg font-black text-primary">{Math.round(opp.match_score)}%</div>
                            <span className="text-[10px] text-muted-foreground uppercase">Fit Score</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {getEligibilityBadge(opp.eligibility_status)}
                          <span className="text-[11px] text-muted-foreground">Stipend: {opp.stipend || 'Competitive'}</span>
                        </div>

                        {opp.strengths && opp.strengths.length > 0 && (
                          <div className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                            ✓ {opp.strengths[0]}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: EXECUTION PLAN */}
          {activeTab === 'plan' && (
            <div className="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-foreground">Gemini Autonomous Execution Plan</h3>
                  <p className="text-xs text-muted-foreground">Sequenced tool invocations formulated specifically for goal</p>
                </div>
                <span className="text-xs text-muted-foreground">{activeRun.execution_plan?.length || 0} Steps</span>
              </div>

              <div className="space-y-3 pt-2">
                {activeRun.execution_plan?.map((step) => {
                  const isDone = step.status === 'completed';
                  const isRun = step.status === 'running';
                  const isFail = step.status === 'failed';
                  return (
                    <div
                      key={step.step}
                      className={`p-4 rounded-xl border transition ${
                        isRun
                          ? 'bg-primary/5 border-primary/40 shadow-sm'
                          : isDone
                          ? 'bg-card border-border/80'
                          : isFail
                          ? 'bg-rose-500/5 border-rose-500/30'
                          : 'bg-muted/20 border-border/40 opacity-70'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5 shrink-0">
                            {isDone ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            ) : isRun ? (
                              <RefreshCw className="w-4 h-4 text-primary animate-spin" />
                            ) : isFail ? (
                              <XCircle className="w-4 h-4 text-rose-500" />
                            ) : (
                              <Circle className="w-4 h-4 text-muted-foreground" />
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-foreground">Step {step.step}: {step.tool}</span>
                              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                                isDone ? 'bg-emerald-500/10 text-emerald-500' : isRun ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                              }`}>
                                {step.status}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
                            {step.result_summary && (
                              <p className="text-xs font-medium text-foreground/90 mt-2 bg-accent/30 p-2 rounded-lg border border-border/40">
                                ➔ {step.result_summary}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: OPPORTUNITIES */}
          {activeTab === 'opportunities' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-foreground">Ranked & Verified Opportunities</h3>
                <span className="text-xs text-muted-foreground">{topOpps.length} opportunities evaluated</span>
              </div>

              <div className="space-y-4">
                {topOpps.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground rounded-2xl bg-card border border-border">
                    No evaluated opportunities found in current run.
                  </div>
                ) : (
                  topOpps.map((opp) => (
                    <div key={opp.internship_id} className="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4 hover:border-primary/30 transition">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border/80">
                        <div>
                          <div className="flex items-center gap-2.5">
                            <h4 className="text-base font-bold text-foreground">{opp.title}</h4>
                            {getEligibilityBadge(opp.eligibility_status)}
                          </div>
                          <p className="text-xs text-muted-foreground font-medium mt-0.5">
                            {opp.company} • {opp.location} • {opp.work_mode} • Stipend: {opp.stipend || 'Competitive'}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <span className="text-2xl font-black text-primary">{Math.round(opp.match_score)}%</span>
                            <p className="text-[10px] text-muted-foreground uppercase font-semibold">Match Score</p>
                          </div>
                        </div>
                      </div>

                      {/* Factor Breakdown & Provenance */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div className="space-y-1.5">
                          <span className="font-bold text-foreground">Strengths & Match Provenance:</span>
                          {opp.strengths && opp.strengths.length > 0 ? (
                            opp.strengths.map((s, idx) => (
                              <p key={idx} className="text-emerald-600 dark:text-emerald-400 font-medium">{s}</p>
                            ))
                          ) : (
                            <p className="text-muted-foreground">General background alignment</p>
                          )}
                        </div>
                        <div className="space-y-1.5">
                          <span className="font-bold text-foreground">Skill Gaps & Missing Requirements:</span>
                          {opp.missing_requirements && opp.missing_requirements.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {opp.missing_requirements.map((m, idx) => (
                                <span key={idx} className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 text-[11px] font-medium">
                                  {m}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-emerald-500">All core technical requirements met</p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                        <span className="text-[11px] text-muted-foreground">Source: {opp.source} • Verified Active</span>
                        <a
                          href={opp.application_url || '#'}
                          target="_blank"
                          rel="noreferrer"
                          className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-accent hover:bg-accent/80 text-foreground transition flex items-center gap-1"
                        >
                          <span>Apply Link</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 4: APPLICATION PACKAGE */}
          {activeTab === 'package' && appPackage && (
            <div className="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-foreground">Prepared Application Package</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3" /> Fact-Validated
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">Target: <strong>{appPackage.company}</strong> — {appPackage.title}</p>
                </div>
                {activeRun.status === 'AWAITING_APPROVAL' && (
                  <button
                    onClick={handleApprove}
                    disabled={isApproving}
                    className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-2 shadow-sm shadow-emerald-600/30"
                  >
                    {isApproving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                    <span>Approve & Mark Ready</span>
                  </button>
                )}
              </div>

              {/* Cover Letter Section */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-foreground">
                  <FileText className="w-4 h-4 text-primary" />
                  <span>Tailored Cover Letter Draft:</span>
                </div>
                <div className="p-4 rounded-xl bg-accent/30 border border-border/80 font-mono text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed">
                  {appPackage.cover_letter_draft}
                </div>
              </div>

              {/* Resume Tailoring Suggestions */}
              {appPackage.resume_tailoring && (
                <div className="space-y-2 pt-4 border-t border-border">
                  <span className="text-xs font-bold text-foreground">Resume Bullet Optimizations:</span>
                  <div className="p-4 rounded-xl bg-accent/30 border border-border/80 text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed">
                    {appPackage.resume_tailoring}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-foreground">Live Agent Activity Log</h3>
                <span className="text-xs text-muted-foreground">{events.length} Events Logged</span>
              </div>

              <div className="space-y-3 pt-2">
                {events.map((ev) => (
                  <div key={ev.id} className="flex items-start gap-3 text-xs p-3 rounded-xl bg-accent/30 border border-border/60">
                    <Clock className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-foreground">{ev.event_type}</span>
                        <span className="text-[10px] text-muted-foreground">{new Date(ev.created_at).toLocaleTimeString()}</span>
                      </div>
                      <p className="text-muted-foreground mt-0.5">{ev.message}</p>
                      {ev.tool_name && (
                        <span className="inline-block text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-primary/10 text-primary mt-1">
                          tool: {ev.tool_name}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentWorkspace;
