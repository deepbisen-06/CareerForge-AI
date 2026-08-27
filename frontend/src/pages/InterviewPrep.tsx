import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Brain, Calendar, Eye, EyeOff, Sparkles, ChevronRight, Mic,
  CheckCircle2, Clock, BookOpen, Loader2, BarChart2, TrendingUp, AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { Internship, InterviewSession, PrepPlan, InterviewProgress } from '../types';

export const InterviewPrep: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const internshipIdParam = searchParams.get('internship_id');

  const [internships, setInternships] = useState<Internship[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number>(internshipIdParam ? parseInt(internshipIdParam) : 1);
  const [activeTab, setActiveTab] = useState<'QUESTIONS' | 'ROADMAP' | 'ANALYTICS'>('QUESTIONS');

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [prepPlan, setPrepPlan] = useState<PrepPlan | null>(null);
  const [progress, setProgress] = useState<InterviewProgress | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [revealedIds, setRevealedIds] = useState<number[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    api.internships.list({ limit: 30 })
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

    Promise.all([
      api.interview.generateQuestions({ internship_id: selectedJobId, count: 8 }),
      api.interview.getPrepPlan(selectedJobId),
      api.interview.getProgress()
    ])
      .then(([sessionData, planData, progData]) => {
        setSession(sessionData);
        setPrepPlan(planData);
        setProgress(progData);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [selectedJobId]);

  const toggleReveal = (qId: number) => {
    setRevealedIds(prev =>
      prev.includes(qId) ? prev.filter(id => id !== qId) : [...prev, qId]
    );
  };

  const categories = ['All', 'Technical', 'Behavioral', 'Resume-based', 'Role-specific', 'HR'];

  const filteredQuestions = session?.questions.filter(q =>
    selectedCategory === 'All' ? true : q.category.toLowerCase() === selectedCategory.toLowerCase()
  ) || [];

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Brain className="w-3.5 h-3.5" /> Technical & Behavioral Preparation
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Interview Preparation Hub</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Role-tailored question banks, 5-day structured roadmaps, and historical analytics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Target Job Selector */}
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

          {/* Launch Live Mock Interview */}
          {session && (
            <button
              onClick={() => navigate(`/mock-interview?session_id=${session.id}`)}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold text-xs hover:opacity-95 transition shadow-md shadow-primary/20 flex items-center gap-1.5 shrink-0"
            >
              <Mic className="w-3.5 h-3.5" /> Launch Mock Interview
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab('QUESTIONS')}
          className={`pb-3 px-4 text-xs font-bold transition flex items-center gap-2 border-b-2 ${
            activeTab === 'QUESTIONS'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Brain className="w-4 h-4" /> Role Question Bank ({session?.questions.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('ROADMAP')}
          className={`pb-3 px-4 text-xs font-bold transition flex items-center gap-2 border-b-2 ${
            activeTab === 'ROADMAP'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Calendar className="w-4 h-4" /> 5-Day Study Roadmap
        </button>

        <button
          onClick={() => setActiveTab('ANALYTICS')}
          className={`pb-3 px-4 text-xs font-bold transition flex items-center gap-2 border-b-2 ${
            activeTab === 'ANALYTICS'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <BarChart2 className="w-4 h-4" /> Progress & Weak Topics
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Generating questions and study plan...</p>
        </div>
      ) : activeTab === 'QUESTIONS' ? (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Category Filter Chips */}
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'bg-card text-muted-foreground hover:text-foreground border border-border'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Questions List */}
          <div className="space-y-4">
            {filteredQuestions.map((q, idx) => {
              const isRevealed = revealedIds.includes(q.id);
              return (
                <div
                  key={q.id}
                  className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">
                          {q.category}
                        </span>
                        <span className="text-xs text-muted-foreground font-medium">
                          Difficulty: {q.difficulty}
                        </span>
                      </div>
                      <h3 className="font-bold text-base text-foreground leading-snug">
                        {idx + 1}. {q.question}
                      </h3>
                    </div>

                    <button
                      onClick={() => toggleReveal(q.id)}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-secondary text-secondary-foreground hover:bg-accent border border-border transition flex items-center gap-1.5 shrink-0 self-start"
                    >
                      {isRevealed ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      {isRevealed ? 'Hide Rubric' : 'Reveal Ideal Answer'}
                    </button>
                  </div>

                  {/* Revealed Answer Rubric */}
                  {isRevealed && (
                    <div className="p-4 rounded-2xl bg-muted/40 border border-border/70 text-xs space-y-2 animate-in fade-in duration-200">
                      <div className="flex items-center gap-1.5 text-primary font-bold text-xs uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5" />
                        Ideal Evaluation Rubric & Sample Concepts
                      </div>
                      <p className="text-muted-foreground leading-relaxed">
                        {q.ideal_answer}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : activeTab === 'ROADMAP' ? (
        /* 5-Day Plan Tab */
        <div className="space-y-4 animate-in fade-in duration-300">
          {prepPlan?.five_day_plan.map((dayPlan) => (
            <div
              key={dayPlan.day}
              className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-base flex items-center gap-2 text-foreground">
                  <span className="w-7 h-7 rounded-xl bg-primary text-primary-foreground font-bold text-xs flex items-center justify-center">
                    {dayPlan.day}
                  </span>
                  {dayPlan.title}
                </h3>
                <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {dayPlan.time_estimate}
                </span>
              </div>

              <div className="space-y-2 pt-2">
                {dayPlan.tasks.map((task, tIdx) => (
                  <div key={tIdx} className="p-3 rounded-2xl bg-background border border-border/60 text-xs flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                    <span className="leading-relaxed text-muted-foreground">{task}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Historical Analytics Tab */
        <div className="space-y-6 animate-in fade-in duration-300">
          {progress && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-5 rounded-2xl border border-border bg-card/60">
                <span className="text-xs font-semibold uppercase text-muted-foreground">Sessions Completed</span>
                <div className="text-2xl font-black text-foreground mt-1">{progress.total_sessions}</div>
                <div className="text-xs text-muted-foreground mt-1">Average Readiness: {progress.average_score}%</div>
              </div>

              <div className="p-5 rounded-2xl border border-border bg-card/60 md:col-span-2">
                <span className="text-xs font-semibold uppercase text-muted-foreground">Category Averages</span>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                  {Object.entries(progress.category_averages).map(([cat, score]) => (
                    <div key={cat} className="p-2.5 rounded-xl bg-background border border-border text-center">
                      <div className="text-[11px] text-muted-foreground truncate">{cat}</div>
                      <div className="text-sm font-black text-primary">{score}/10</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {progress?.recurring_weak_topics && progress.recurring_weak_topics.length > 0 && (
            <div className="p-6 rounded-3xl bg-amber-500/5 border border-amber-500/20 space-y-3">
              <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>Frequently Missed Technical Concepts across Sessions</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {progress.recurring_weak_topics.map((topic) => (
                  <span key={topic} className="px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/20">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InterviewPrep;
