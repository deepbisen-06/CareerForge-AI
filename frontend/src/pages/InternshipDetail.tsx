import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Sparkles, CheckCircle2, AlertTriangle, Briefcase, MapPin, DollarSign,
  Clock, Award, ExternalLink, Bookmark, FileText, Mic, Brain, ArrowLeft,
  Loader2, Check, Shield, ThumbsUp, ThumbsDown
} from 'lucide-react';
import { api } from '../services/api';
import { Internship, MatchExplanation } from '../types';

export const InternshipDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [internship, setInternship] = useState<Internship | null>(null);
  const [match, setMatch] = useState<MatchExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<'UP' | 'DOWN' | null>(null);

  useEffect(() => {
    if (!id) return;
    const internshipId = parseInt(id);

    Promise.all([
      api.internships.get(internshipId),
      api.matching.getExplanation(internshipId)
    ])
      .then(([jobData, matchData]) => {
        setInternship(jobData);
        setMatch(matchData);
        setIsSaved(Boolean(jobData.is_saved));
      })
      .catch((err) => console.error("Error loading internship detail:", err))
      .finally(() => setIsLoading(false));
  }, [id]);

  const handleToggleSave = async () => {
    if (!internship) return;
    try {
      if (isSaved) {
        await api.internships.unsave(internship.id);
        setIsSaved(false);
      } else {
        await api.internships.save(internship.id);
        setIsSaved(true);
      }
    } catch (err) {
      console.error("Error toggling saved:", err);
    }
  };

  const handleFeedback = async (isPositive: boolean) => {
    if (!internship) return;
    try {
      await api.matching.submitFeedback({
        internship_id: internship.id,
        is_positive: isPositive,
        reason_category: isPositive ? 'GOOD_RECOMMENDATION' : 'SKILL_MISMATCH'
      });
      setFeedbackSent(isPositive ? 'UP' : 'DOWN');
    } catch (err) {
      console.error("Feedback error:", err);
    }
  };

  if (isLoading || !internship || !match) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Calculating explainable match breakdown & skill gaps...</p>
        </div>
      </div>
    );
  }

  const breakdown = match.score_breakdown;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Back Button */}
      <button
        onClick={() => navigate('/internships')}
        className="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Explorer
      </button>

      {/* Main Internship Header Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              {internship.company_logo_url ? (
                <img
                  src={internship.company_logo_url}
                  alt=""
                  className="w-12 h-12 object-contain rounded-xl p-1 bg-muted/40 shrink-0"
                />
              ) : (
                <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-black text-lg shrink-0">
                  {internship.company[0]}
                </div>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-primary px-3 py-0.5 rounded-full bg-primary/10 border border-primary/20">
                    {internship.company}
                  </span>
                  <span className="text-xs text-muted-foreground font-medium">{internship.domain}</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground mt-1">
                  {internship.title}
                </h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pt-1">
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {internship.location}</span>
              <span className="flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" /> {internship.work_mode}</span>
              <span className="flex items-center gap-1"><DollarSign className="w-3.5 h-3.5" /> {internship.stipend || 'Competitive'}</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Deadline: {internship.deadline || 'Upcoming'}</span>
            </div>
          </div>

          {/* Big Match Badge & Feedback */}
          <div className="p-4 px-6 rounded-3xl bg-gradient-to-tr from-emerald-500/15 via-teal-500/10 to-transparent border border-emerald-500/30 text-center shrink-0">
            <div className="text-3xl sm:text-4xl font-black text-emerald-600 dark:text-emerald-400">
              {match.overall_score}%
            </div>
            <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">Compatibility Match</p>
            <p className="text-[10px] text-muted-foreground mb-3">Deterministic 6-Factor AI</p>

            <div className="flex items-center justify-center gap-2 pt-2 border-t border-emerald-500/20">
              <button
                onClick={() => handleFeedback(true)}
                disabled={feedbackSent !== null}
                className={`p-1.5 rounded-lg border transition ${
                  feedbackSent === 'UP'
                    ? 'bg-emerald-500 text-white border-emerald-500'
                    : 'hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                }`}
                title="Good Recommendation"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                disabled={feedbackSent !== null}
                className={`p-1.5 rounded-lg border transition ${
                  feedbackSent === 'DOWN'
                    ? 'bg-rose-500 text-white border-rose-500'
                    : 'hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 border-rose-500/30'
                }`}
                title="Poor Recommendation"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Action Button Bar */}
        <div className="pt-4 border-t border-border/80 flex flex-wrap items-center gap-2.5">
          {internship.application_url && (
            <a
              href={internship.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition flex items-center gap-1.5 shadow-md shadow-primary/20"
            >
              Apply on Portal <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}

          <button
            onClick={handleToggleSave}
            className={`px-4 py-2 rounded-xl text-xs font-semibold border transition flex items-center gap-1.5 ${
              isSaved
                ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                : 'bg-secondary text-secondary-foreground hover:bg-accent border-border'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            {isSaved ? 'Bookmarked in Saved Jobs' : 'Bookmark Opportunity'}
          </button>

          <button
            onClick={() => navigate(`/documents?internship_id=${internship.id}`)}
            className="px-4 py-2 rounded-xl bg-secondary text-secondary-foreground hover:bg-accent font-semibold text-xs border border-border transition flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5" /> Customize Resume & Cover Letter
          </button>

          <button
            onClick={() => navigate(`/interview-prep?internship_id=${internship.id}`)}
            className="px-4 py-2 rounded-xl bg-secondary text-secondary-foreground hover:bg-accent font-semibold text-xs border border-border transition flex items-center gap-1.5"
          >
            <Brain className="w-3.5 h-3.5" /> Prepare Interview
          </button>
        </div>
      </div>

      {/* 360-Degree Explainable Compatibility Breakdown */}
      <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-6">
        <div>
          <h2 className="text-lg font-bold tracking-tight flex items-center gap-2 text-foreground">
            <Award className="w-5 h-5 text-primary" />
            360° Explainable Compatibility Breakdown
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Transparent deterministic weights calculated without generative hallucination.
          </p>
        </div>

        {/* 6 Dimension Progress Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Skills 30% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Technical Skills Match (30% Weight)</span>
              <span className="text-primary">{breakdown.skills_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{ width: `${breakdown.skills_score}%` }} />
            </div>
          </div>

          {/* Experience 20% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Experience & Internships (20% Weight)</span>
              <span className="text-indigo-500">{breakdown.experience_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${breakdown.experience_score}%` }} />
            </div>
          </div>

          {/* Projects 15% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Projects Portfolio Alignment (15% Weight)</span>
              <span className="text-violet-500">{breakdown.projects_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-violet-500 h-2 rounded-full" style={{ width: `${breakdown.projects_score}%` }} />
            </div>
          </div>

          {/* Education 15% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Education & Major (15% Weight)</span>
              <span className="text-emerald-500">{breakdown.education_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${breakdown.education_score}%` }} />
            </div>
          </div>

          {/* Eligibility 10% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Graduation & Eligibility (10% Weight)</span>
              <span className="text-teal-500">{breakdown.eligibility_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-teal-500 h-2 rounded-full" style={{ width: `${breakdown.eligibility_score}%` }} />
            </div>
          </div>

          {/* Preferences 10% */}
          <div className="p-4 rounded-2xl bg-background border border-border/70 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span>Student Preferences Alignment (10% Weight)</span>
              <span className="text-amber-500">{breakdown.preference_score}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${breakdown.preference_score}%` }} />
            </div>
          </div>
        </div>

        {/* AI Recommendation & Auditable Reasoning */}
        <div className="p-5 rounded-2xl bg-primary/5 border border-primary/20 space-y-2">
          <div className="flex items-center gap-2 text-primary font-bold text-xs">
            <Sparkles className="w-4 h-4" />
            <span>AI MATCH VERDICT: {match.recommendation}</span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {match.reasoning}
          </p>
        </div>
      </div>

      {/* Why You Match vs Identified Discrepancies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Why You Match */}
        <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-4">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>Why You Match (Strengths)</span>
          </div>
          <div className="space-y-2">
            {match.strengths.map((st, idx) => (
              <div key={idx} className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/15 text-xs flex items-start gap-2">
                <span className="text-emerald-500 font-bold">✓</span>
                <span className="leading-relaxed text-foreground">{st}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Identified Discrepancies & Gaps */}
        <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-4">
          <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5" />
            <span>Identified Discrepancies & Gaps</span>
          </div>
          <div className="space-y-2">
            {match.discrepancies && match.discrepancies.length > 0 ? (
              match.discrepancies.map((disc, idx) => (
                <div key={idx} className="p-3 rounded-2xl bg-rose-500/5 border border-rose-500/15 text-xs flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2">
                    <span className="text-rose-500 font-bold">⚠</span>
                    <span className="text-foreground">{disc}</span>
                  </div>
                </div>
              ))
            ) : match.missing_skills.length === 0 ? (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-600">
                You satisfy all primary required skills for this position!
              </div>
            ) : (
              match.missing_skills.map((ms, idx) => (
                <div key={idx} className="p-3 rounded-2xl bg-rose-500/5 border border-rose-500/15 text-xs flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2">
                    <span className="text-rose-500 font-bold">⚠</span>
                    <span>Missing skill: <strong>{ms}</strong></span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 shrink-0">
                    GAP
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Full Job Description & Requirements */}
      <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-foreground">Job Description & Responsibilities</h2>
        <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-line">
          {internship.description}
        </p>

        <div className="pt-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">Eligibility Criteria</h3>
          <p className="text-xs text-foreground bg-muted/40 p-3 rounded-xl border border-border/70">
            {internship.eligibility || 'Open to all STEM undergraduates and postgraduates.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default InternshipDetail;
