import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles, ArrowRight, CheckCircle2, AlertTriangle, Clock, Briefcase,
  TrendingUp, Award, FileText, ChevronRight, BarChart2, BookOpen, Mic, Bookmark
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardOverview, Internship } from '../types';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.dashboard.getOverview()
      .then(setData)
      .catch((err) => console.error("Error loading dashboard overview:", err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-medium text-muted-foreground animate-pulse">
            Loading Career Intelligence Dashboard...
          </p>
        </div>
      </div>
    );
  }

  const overview = data || {
    user_name: 'Student',
    profile_completion: 85,
    resume_score: 86.0,
    total_applications: 3,
    saved_jobs_count: 2,
    status_counts: { SAVED: 1, APPLIED: 1, INTERVIEW: 1 },
    top_recommendations: [],
    high_priority_gaps: [],
    upcoming_deadlines: [],
    interview_readiness: 78.0,
    notifications_unread: 0
  };

  const funnel = overview.funnel_metrics || {
    saved: overview.saved_jobs_count || 1,
    planned: 0,
    applied: 1,
    assessment: 0,
    interview: 1,
    offer: 0,
    selected: 0,
    rejected: 0,
    interview_rate_pct: 50.0,
    offer_rate_pct: 0.0
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary via-primary/90 to-accent p-6 md:p-8 text-primary-foreground shadow-xl shadow-primary/20">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-background/20 backdrop-blur text-xs font-semibold border border-background/25">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            AI Career Pipeline Active
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Welcome back, {overview.user_name}!
          </h1>
          <p className="text-primary-foreground/85 text-sm leading-relaxed">
            Your candidate profile is matched against 1,000+ verified opportunities. Review your high-compatibility matches, bridge skill gaps, and simulate voice mock interviews.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/internships"
              className="px-4 py-2 rounded-xl bg-background text-foreground font-bold text-xs hover:bg-background/90 transition shadow-md flex items-center gap-1.5"
            >
              Explore Matches <ChevronRight className="w-4 h-4" />
            </Link>
            <Link
              to="/resume-studio"
              className="px-4 py-2 rounded-xl bg-background/20 hover:bg-background/30 backdrop-blur font-semibold text-xs border border-background/30 transition flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5" /> Resume Health
            </Link>
          </div>
        </div>

        {/* Decorative Circles */}
        <div className="absolute -right-10 -bottom-10 w-72 h-72 rounded-full bg-white/10 blur-2xl pointer-events-none" />
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Resume ATS Score */}
        <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Resume ATS Score</span>
            <span className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <Award className="w-4 h-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-foreground">{overview.resume_score || 86}</span>
            <span className="text-xs text-muted-foreground font-medium">/ 100</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${overview.resume_score || 86}%` }}
            />
          </div>
          <p className="text-[11px] text-muted-foreground flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" /> Strong keyword density & impact metrics
          </p>
        </div>

        {/* Profile Completion */}
        <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Profile Readiness</span>
            <span className="p-2 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
              <TrendingUp className="w-4 h-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-foreground">{overview.profile_completion}%</span>
            <span className="text-xs text-emerald-600 font-semibold">Active</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-500"
              style={{ width: `${overview.profile_completion}%` }}
            />
          </div>
          <Link to="/profile-wizard" className="text-[11px] text-primary font-medium hover:underline flex items-center gap-0.5">
            Update student profile <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        {/* Interview Readiness */}
        <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Interview Readiness</span>
            <span className="p-2 rounded-xl bg-violet-500/10 text-violet-600 dark:text-violet-400">
              <Mic className="w-4 h-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-foreground">{overview.interview_readiness}%</span>
            <span className="text-xs text-violet-600 font-semibold">Live AI Rubric</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div
              className="bg-accent h-2 rounded-full transition-all duration-500"
              style={{ width: `${overview.interview_readiness}%` }}
            />
          </div>
          <Link to="/mock-interview" className="text-[11px] text-accent font-medium hover:underline flex items-center gap-0.5">
            Launch Voice Simulation <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        {/* Saved & Tracked Applications */}
        <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Saved & In-Pipeline</span>
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <Bookmark className="w-4 h-4" />
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-foreground">
              {(overview.saved_jobs_count || 0) + overview.total_applications}
            </span>
            <span className="text-xs text-muted-foreground">
              ({overview.saved_jobs_count || 0} saved, {overview.total_applications} applied)
            </span>
          </div>
          <div className="flex gap-1 h-2 rounded-full overflow-hidden bg-muted">
            <div className="bg-blue-500 flex-1" title="Saved" />
            <div className="bg-indigo-500 flex-1" title="Applied" />
            <div className="bg-purple-500 flex-1" title="Interview" />
          </div>
          <Link to="/saved-jobs" className="text-[11px] text-primary font-medium hover:underline flex items-center gap-0.5">
            View Bookmarked Roles <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Conversion Funnel Analytics Card */}
      <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-bold text-base text-foreground flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-primary" /> Application Conversion Funnel Analytics
            </h3>
            <p className="text-xs text-muted-foreground">Real-time candidate conversion telemetry from saved to offer</p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">
              Interview Conversion: {funnel.interview_rate_pct}%
            </span>
            <span className="text-primary font-bold">
              Offer Conversion: {funnel.offer_rate_pct}%
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 pt-2">
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Saved</span>
            <p className="text-lg font-black text-foreground mt-0.5">{funnel.saved}</p>
          </div>
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Applied</span>
            <p className="text-lg font-black text-primary mt-0.5">{funnel.applied}</p>
          </div>
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Assessment</span>
            <p className="text-lg font-black text-indigo-500 mt-0.5">{funnel.assessment}</p>
          </div>
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Interview</span>
            <p className="text-lg font-black text-violet-500 mt-0.5">{funnel.interview}</p>
          </div>
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Offer</span>
            <p className="text-lg font-black text-emerald-500 mt-0.5">{funnel.offer + funnel.selected}</p>
          </div>
          <div className="p-3 rounded-2xl bg-background border border-border text-center">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">Rejected</span>
            <p className="text-lg font-black text-rose-500 mt-0.5">{funnel.rejected}</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Top Recommended Matches & Deadlines/Skill Gaps */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Top Recommendations */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold tracking-tight text-foreground">Top AI Recommendations</h2>
              <p className="text-xs text-muted-foreground">Ranked by 6-factor deterministic compatibility</p>
            </div>
            <Link
              to="/internships"
              className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
            >
              View 1,000+ roles <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3.5">
            {overview.top_recommendations.map((job) => (
              <div
                key={job.id}
                className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 hover:border-primary/40 transition-all shadow-sm space-y-3"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    {job.company_logo_url ? (
                      <img src={job.company_logo_url} alt="" className="w-10 h-10 object-contain rounded-xl p-1 bg-muted/40 shrink-0" />
                    ) : (
                      <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0">
                        {job.company[0]}
                      </div>
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-primary">
                          {job.company}
                        </span>
                        <span className="text-[11px] text-muted-foreground">{job.domain}</span>
                      </div>
                      <h3 className="font-bold text-base mt-0.5 text-foreground">{job.title}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {job.location} • {job.work_mode} • {job.stipend || 'Competitive'}
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="px-3 py-1 rounded-2xl bg-gradient-to-r from-emerald-500/15 to-teal-500/15 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-extrabold text-sm">
                      {job.match_score || 88}% Match
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-1">Deterministic AI</p>
                  </div>
                </div>

                {/* Skill Chips */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {job.requirements.slice(0, 4).map((req, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 text-[11px] font-medium rounded-md bg-secondary text-secondary-foreground"
                    >
                      {req}
                    </span>
                  ))}
                </div>

                {/* Action Buttons */}
                <div className="pt-2 border-t border-border/60 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> Deadline: {job.deadline || 'Upcoming'}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => navigate(`/internships/${job.id}`)}
                      className="px-3 py-1.5 rounded-xl text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition shadow-sm"
                    >
                      Match Breakdown
                    </button>
                    <button
                      onClick={() => navigate(`/documents?internship_id=${job.id}`)}
                      className="px-3 py-1.5 rounded-xl text-xs font-medium bg-secondary text-secondary-foreground hover:bg-accent transition"
                    >
                      Tailor Resume
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Column: Skill Gaps & Deadlines */}
        <div className="space-y-6">
          {/* Skill Gaps Summary */}
          <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-foreground">Identified Skill Gaps</h3>
                <p className="text-[11px] text-muted-foreground">Critical areas to level up before applying</p>
              </div>
              <Link to="/skill-gaps" className="text-xs font-semibold text-primary hover:underline">
                Roadmap
              </Link>
            </div>

            <div className="space-y-2.5">
              {overview.high_priority_gaps.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No critical skill gaps identified!</p>
              ) : (
                overview.high_priority_gaps.map((gap, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-2xl bg-background border border-border/70 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-foreground">{gap.skill}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 border border-rose-500/20">
                        {gap.status_tag || 'HIGH GAP'}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-[11px] leading-relaxed">
                      {gap.recommendation}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Upcoming Deadlines */}
          <div className="p-5 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-foreground">Approaching Deadlines</h3>
                <p className="text-[11px] text-muted-foreground">Keep your applications on schedule</p>
              </div>
              <Link to="/applications" className="text-xs font-semibold text-primary hover:underline">
                Tracker
              </Link>
            </div>

            <div className="space-y-2.5">
              {overview.upcoming_deadlines.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No urgent deadlines approaching.</p>
              ) : (
                overview.upcoming_deadlines.map((app) => (
                  <div
                    key={app.id}
                    className="p-3 rounded-2xl bg-background border border-border/70 text-xs flex items-center justify-between"
                  >
                    <div>
                      <p className="font-bold text-foreground">{app.internship.company}</p>
                      <p className="text-[11px] text-muted-foreground">{app.internship.title}</p>
                    </div>
                    <div className="text-right">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">
                        {app.deadline || 'Pending'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
