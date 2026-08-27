import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Mic, MicOff, Send, Bot, User, Sparkles, Award, CheckCircle2,
  ChevronRight, ArrowRight, RotateCcw, Loader2, BarChart2, AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { InterviewSession, InterviewQuestion } from '../types';

export const MockInterview: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionIdParam = searchParams.get('session_id');
  const internshipIdParam = searchParams.get('internship_id');

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answerText, setAnswerText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initSession = async () => {
      setIsLoading(true);
      try {
        if (sessionIdParam) {
          const s = await api.interview.getSession(parseInt(sessionIdParam));
          setSession(s);
        } else {
          let targetJobId = internshipIdParam ? parseInt(internshipIdParam) : null;
          if (!targetJobId) {
            const jobs = await api.internships.list({ limit: 1 });
            targetJobId = jobs.length > 0 ? jobs[0].id : 1;
          }
          const s = await api.interview.generateQuestions({ internship_id: targetJobId, count: 6 });
          setSession(s);
        }
      } catch (err) {
        console.error("Error creating interview session:", err);
      } finally {
        setIsLoading(false);
      }
    };
    initSession();
  }, [sessionIdParam, internshipIdParam]);

  const currentQuestion: InterviewQuestion | undefined = session?.questions[currentQIndex];

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !answerText.trim() || isSubmitting) return;
    setIsSubmitting(true);

    try {
      const updatedQ = await api.interview.submitAnswer({
        question_id: currentQuestion.id,
        user_answer: answerText
      });
      
      setSession(prev => {
        if (!prev) return prev;
        const newQuestions = prev.questions.map(q => q.id === updatedQ.id ? updatedQ : q);
        const answered = newQuestions.filter(q => q.score !== undefined && q.score !== null);
        const avg = answered.reduce((acc, q) => acc + (q.score || 0), 0) / (answered.length || 1);
        return {
          ...prev,
          score: round(avg, 1),
          readiness_score: round(avg * 10, 1),
          questions: newQuestions
        };
      });

      setAnswerText('');
      if (session && currentQIndex === session.questions.length - 1) {
        setSessionComplete(true);
      }
    } catch (err) {
      console.error("Error submitting answer:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const round = (num: number, dec: number) => Number(num.toFixed(dec));

  const toggleSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please type your answer.");
      return;
    }

    if (isListening) {
      setIsListening(false);
    } else {
      setIsListening(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setAnswerText(prev => prev ? `${prev} ${transcript}` : transcript);
        setIsListening(false);
      };

      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognition.start();
    }
  };

  if (isLoading || !session || !currentQuestion) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Initializing AI Mock Interview Studio...</p>
        </div>
      </div>
    );
  }

  const answeredCount = session.questions.filter(q => q.score !== undefined && q.score !== null).length;

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 text-violet-600 dark:text-violet-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Mic className="w-3.5 h-3.5" /> Voice-Enabled Live Simulation
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">AI Mock Interview Studio</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Target Role: <strong className="text-foreground">{session.role_title || 'Software Engineering Intern'}</strong>
          </p>
        </div>

        {/* Readiness Score Gauge */}
        <div className="p-4 px-6 rounded-2xl bg-card/60 backdrop-blur-sm border border-border shadow-sm flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-primary to-accent text-primary-foreground font-black text-base flex items-center justify-center shadow-md">
            {session.readiness_score || 0}%
          </div>
          <div>
            <p className="text-xs font-bold text-foreground">Live Readiness</p>
            <p className="text-[11px] text-muted-foreground">{answeredCount} of {session.questions.length} answered</p>
          </div>
        </div>
      </div>

      {!sessionComplete ? (
        <div className="space-y-6">
          {/* Question Index Dots Bar */}
          <div className="flex items-center gap-2 pb-2 overflow-x-auto">
            {session.questions.map((q, idx) => {
              const isCurrent = idx === currentQIndex;
              const isAnswered = q.score !== undefined && q.score !== null;
              return (
                <button
                  key={q.id}
                  onClick={() => setCurrentQIndex(idx)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                    isCurrent
                      ? 'bg-primary text-primary-foreground shadow-md shadow-primary/20'
                      : isAnswered
                      ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                      : 'bg-card text-muted-foreground hover:text-foreground border border-border'
                  }`}
                >
                  {isAnswered && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />}
                  <span>Q{idx + 1}</span>
                </button>
              );
            })}
          </div>

          {/* Question Card */}
          <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-primary/10 text-primary border border-primary/20">
                {currentQuestion.category}
              </span>
              <span className="text-xs text-muted-foreground font-medium">Difficulty: {currentQuestion.difficulty}</span>
            </div>

            <h2 className="text-lg sm:text-xl font-bold leading-relaxed text-foreground">
              {currentQuestion.question}
            </h2>
          </div>

          {/* If Question is already graded, show live Rubric breakdown */}
          {currentQuestion.score !== undefined && currentQuestion.score !== null && (
            <div className="p-6 rounded-3xl bg-card/80 border border-emerald-500/30 space-y-5 animate-in fade-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-base">
                  <CheckCircle2 className="w-5 h-5" />
                  <span>AI Objective Evaluation: {currentQuestion.score} / 10.0</span>
                </div>
              </div>

              {/* 4 Dimension Criteria Grid */}
              {currentQuestion.evaluation_criteria && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3.5 rounded-2xl bg-background border border-border text-center">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Technical Accuracy</span>
                    <p className="text-lg font-black text-primary mt-0.5">{currentQuestion.evaluation_criteria.accuracy || 8.5}/10</p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-background border border-border text-center">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Clarity & Comm</span>
                    <p className="text-lg font-black text-indigo-500 mt-0.5">{currentQuestion.evaluation_criteria.clarity || 8.0}/10</p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-background border border-border text-center">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Relevance</span>
                    <p className="text-lg font-black text-violet-500 mt-0.5">{currentQuestion.evaluation_criteria.relevance || 9.0}/10</p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-background border border-border text-center">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Confidence</span>
                    <p className="text-lg font-black text-emerald-500 mt-0.5">{currentQuestion.evaluation_criteria.confidence || 8.5}/10</p>
                  </div>
                </div>
              )}

              {/* Concept Hits & Misses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {currentQuestion.detected_concepts && currentQuestion.detected_concepts.length > 0 && (
                  <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400">
                    <div className="font-bold mb-1 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Detected Core Concepts:
                    </div>
                    <p>{currentQuestion.detected_concepts.join(', ')}</p>
                  </div>
                )}
                {currentQuestion.missing_concepts && currentQuestion.missing_concepts.length > 0 && (
                  <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400">
                    <div className="font-bold mb-1 flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5" /> Suggested Key Concepts:
                    </div>
                    <p>{currentQuestion.missing_concepts.join(', ')}</p>
                  </div>
                )}
              </div>

              <div className="p-4 rounded-2xl bg-muted/40 border border-border/80 text-xs text-muted-foreground leading-relaxed">
                <strong className="text-foreground">Feedback:</strong> {currentQuestion.feedback}
              </div>

              {currentQIndex < session.questions.length - 1 && (
                <button
                  onClick={() => setCurrentQIndex(prev => prev + 1)}
                  className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center gap-2 shadow-md shadow-primary/20"
                >
                  Proceed to Next Question <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Answer Input Area */}
          <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Your Answer (Type or Speak)
              </label>

              <button
                type="button"
                onClick={toggleSpeechRecognition}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                  isListening
                    ? 'bg-rose-500 text-white animate-pulse shadow-md shadow-rose-500/30'
                    : 'bg-secondary text-secondary-foreground hover:bg-accent border border-border'
                }`}
              >
                {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-primary" />}
                <span>{isListening ? 'Listening via Microphone...' : 'Speak Answer'}</span>
              </button>
            </div>

            <textarea
              rows={5}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              placeholder="Explain your approach, architectural decisions, and specific technologies using the STAR framework..."
              disabled={isSubmitting}
              className="w-full bg-background border border-input rounded-2xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 leading-relaxed"
            />

            <div className="flex items-center justify-between pt-2">
              <p className="text-xs text-muted-foreground">
                Tip: Quantify your results and explain trade-off rationale.
              </p>

              <button
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim() || isSubmitting}
                className="px-6 py-2.5 rounded-xl font-semibold text-xs bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center gap-2 shadow-md shadow-primary/20 disabled:opacity-40"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>Submit for Evaluation</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Completed Session Review */
        <div className="p-8 rounded-3xl bg-card border border-border shadow-xl text-center space-y-6 animate-in zoom-in-95">
          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-white font-black text-3xl mx-auto shadow-lg shadow-emerald-500/20">
            {session.readiness_score}%
          </div>

          <div className="space-y-1">
            <h2 className="text-2xl font-black text-foreground">Mock Interview Session Completed!</h2>
            <p className="text-sm text-muted-foreground">
              Overall Candidate Readiness Score: <strong className="text-foreground">{session.readiness_score}%</strong>
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-muted/40 border border-border text-xs leading-relaxed max-w-md mx-auto text-muted-foreground">
            {session.feedback_summary || 'Strong performance across technical and behavioral questions.'}
          </div>

          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={() => { setSessionComplete(false); setCurrentQIndex(0); }}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-secondary text-secondary-foreground hover:bg-accent border border-border transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Review Questions
            </button>
            <button
              onClick={() => navigate('/interview-prep')}
              className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center gap-1.5 shadow-md shadow-primary/20"
            >
              View Prep Roadmap <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MockInterview;
