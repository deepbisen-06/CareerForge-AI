import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  AlertTriangle, BookOpen, Clock, CheckCircle2, Sparkles, ExternalLink,
  ChevronRight, ArrowRight, Loader2, Award, Zap
} from 'lucide-react';
import { api } from '../services/api';
import { SkillGapReport, Internship } from '../types';

export const SkillGapRoadmap: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const internshipIdParam = searchParams.get('internship_id');

  const [internships, setInternships] = useState<Internship[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number>(internshipIdParam ? parseInt(internshipIdParam) : 1);
  const [report, setReport] = useState<SkillGapReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.internships.list({ limit: 50 })
      .then((jobs) => {
        setInternships(jobs);
        if (!internshipIdParam && jobs.length > 0) {
          setSelectedJobId(jobs[0].id);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedJobId) return;
    setIsLoading(true);
    api.skillGaps.analyze(selectedJobId)
      .then(setReport)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [selectedJobId]);

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Zap className="w-3.5 h-3.5" /> AI Skill Gap Taxonomy & Milestones
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">
            Skill Gap Matrix & Upskilling Roadmap
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Identify priority technical gaps and access targeted learning pathways to maximize interview readiness.
          </p>
        </div>

        {/* Job Selector Dropdown */}
        <select
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(parseInt(e.target.value))}
          className="bg-card border border-border rounded-xl px-4 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/40 shadow-sm"
        >
          {internships.map((job) => (
            <option key={job.id} value={job.id}>
              {job.company} — {job.title}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Synthesizing skill gap analysis & learning roadmap...</p>
        </div>
      ) : report ? (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Target Role & Readiness Banner */}
          <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center sm:text-left">
              <span className="text-xs font-bold text-primary px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
                {report.company}
              </span>
              <h2 className="text-xl sm:text-2xl font-bold mt-2 text-foreground">{report.title}</h2>
              <p className="text-xs text-muted-foreground">
                Target Role Skill Gap Breakdown • {report.total_gaps} identified learning opportunities
              </p>
            </div>

            <div className="p-4 px-6 rounded-3xl bg-gradient-to-tr from-primary/15 to-accent/15 border border-primary/30 text-center shrink-0">
              <div className="text-3xl sm:text-4xl font-black text-primary">
                {report.overall_readiness}%
              </div>
              <p className="text-xs font-bold text-foreground mt-0.5">Role Skill Alignment</p>
              <p className="text-[10px] text-muted-foreground">{report.high_priority_gaps} High Priority Gaps</p>
            </div>
          </div>

          {/* Action Plan Milestones */}
          {report.action_plan && report.action_plan.length > 0 && (
            <div className="p-6 rounded-3xl bg-primary/5 border border-primary/20 space-y-3">
              <div className="flex items-center gap-2 text-primary font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>Personalized 3-Phase Upskilling Strategy</span>
              </div>
              <div className="space-y-2">
                {report.action_plan.map((phase, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-card border border-border/70 text-xs flex items-center gap-2.5">
                    <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground font-bold text-[10px] flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed text-foreground">{phase}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Skill Gap Cards Grid */}
          <div className="space-y-4">
            <h3 className="font-bold text-base text-foreground flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary" />
              Prioritized Skill Gaps & Curated Learning Pathways ({report.gaps.length})
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.gaps.map((gap, idx) => {
                const isHigh = gap.priority === 'HIGH';
                return (
                  <div
                    key={idx}
                    className={`p-5 rounded-3xl bg-card/60 backdrop-blur-sm border transition-all space-y-3 flex flex-col justify-between ${
                      isHigh
                        ? 'border-rose-500/30 hover:border-rose-500/50'
                        : 'border-border/80 hover:border-primary/40'
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-base text-foreground">{gap.skill}</h4>
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                            isHigh
                              ? 'bg-rose-500/10 text-rose-600 border-rose-500/20'
                              : 'bg-amber-500/10 text-amber-600 border-amber-500/20'
                          }`}
                        >
                          {gap.priority} PRIORITY ({gap.status_tag || 'GAP'})
                        </span>
                      </div>

                      <div className="text-xs text-muted-foreground space-y-1">
                        <div className="flex justify-between">
                          <span>Current Level: <strong>{gap.current_level}</strong></span>
                          <span>Target: <strong>{gap.required_level}</strong></span>
                        </div>
                        <p className="pt-1 text-foreground leading-relaxed">
                          {gap.recommendation}
                        </p>
                      </div>
                    </div>

                    {/* Resources & Time */}
                    <div className="pt-3 border-t border-border/60 space-y-2">
                      <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Est. {gap.estimated_hours} Hours
                        </span>
                        <span className="font-semibold text-primary">Curated Docs & Labs</span>
                      </div>

                      {gap.learning_resources && gap.learning_resources.length > 0 && (
                        <div className="space-y-1">
                          {gap.learning_resources.map((res, rIdx) => (
                            <a
                              key={rIdx}
                              href={res.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 rounded-xl bg-background border border-border/60 text-xs font-medium text-primary hover:underline flex items-center justify-between transition"
                            >
                              <span className="truncate">{res.title}</span>
                              <ExternalLink className="w-3 h-3 shrink-0 ml-1 opacity-70" />
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SkillGapRoadmap;
