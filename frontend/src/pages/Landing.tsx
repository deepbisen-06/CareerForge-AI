import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Search,
  ShieldCheck,
  Mic,
  Briefcase,
  Layers,
  ArrowRight,
  TrendingUp,
  FileCheck2,
  Cpu,
  GraduationCap,
  Users,
  Compass,
  Building2,
  CheckCircle2
} from 'lucide-react';

const EMPLOYER_LOGOS = [
  { name: 'Google', logo: 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg' },
  { name: 'Microsoft', logo: 'https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg' },
  { name: 'NVIDIA', logo: 'https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg' },
  { name: 'Amazon', logo: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg' },
  { name: 'Infosys', logo: 'https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg' },
  { name: 'TCS', logo: 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg' },
  { name: 'Swiggy', logo: 'https://upload.wikimedia.org/wikipedia/commons/1/13/Swiggy_logo.svg' },
  { name: 'Zomato', logo: 'https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg' },
  { name: 'Razorpay', logo: 'https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg' },
  { name: 'Zoho', logo: 'https://upload.wikimedia.org/wikipedia/commons/6/69/Zoho_Corporation_logo.png' }
];

const FEATURES = [
  {
    icon: Search,
    title: 'Hybrid Dense + BM25 RAG Search',
    description: 'Combines semantic vector embeddings with keyword retrieval to uncover tailored opportunities matching your exact skills and domain.'
  },
  {
    icon: Layers,
    title: 'Explainable Multi-Factor Matching',
    description: 'Deterministic 6-factor mathematical scoring with 100% transparency. Know precisely why you match and what gaps to close.'
  },
  {
    icon: ShieldCheck,
    title: 'Anti-Hallucination Resume Studio',
    description: 'Fact-validated ATS resume tailoring that reorders genuine achievements without fabricating unverified credentials or experience.'
  },
  {
    icon: Mic,
    title: 'Voice-Enabled AI Mock Interviews',
    description: 'Real-time turn-by-turn spoken interviews evaluating technical precision, concept coverage, clarity, and communication.'
  },
  {
    icon: TrendingUp,
    title: 'Skill Gap Roadmaps & Curated Labs',
    description: 'Tri-state gap classification with personalized 3-phase action plans connected directly to official docs and interactive labs.'
  },
  {
    icon: Briefcase,
    title: 'Intelligent Application Kanban',
    description: 'Manage submissions from initial bookmark to final offer with deadline urgency alerts and conversion funnel analytics.'
  }
];

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col selection:bg-primary/20 selection:text-primary">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-border/40 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground font-bold text-xl shadow-md shadow-primary/20">
              CB
            </div>
            <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              CareerBridge AI
            </span>
          </div>

          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-3 py-2"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-md shadow-primary/20 hover:shadow-lg"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
          {/* Subtle Ambient Gradients */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-primary/15 blur-[120px] rounded-full pointer-events-none -z-10" />
          <div className="absolute top-1/3 right-10 w-[400px] h-[300px] bg-accent/15 blur-[100px] rounded-full pointer-events-none -z-10" />

          <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-6 animate-pulse">
              <Sparkles className="w-3.5 h-3.5" /> Next-Generation AI Internship Application Agent
            </div>

            <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-balance leading-tight sm:leading-none mb-6">
              Land Your Dream Tech Internship with{' '}
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent bg-300% animate-gradient">
                Explainable AI
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
              CareerBridge AI pairs cutting-edge Hybrid RAG semantic retrieval, auditable multi-factor compatibility scoring, factual resume tailoring, and voice-enabled mock interviews into one unified career acceleration platform.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                to="/register"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-primary text-primary-foreground font-semibold text-base shadow-lg shadow-primary/25 hover:bg-primary/90 hover:scale-[1.02] transition-all flex items-center justify-center gap-2"
              >
                Launch Your Career <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl border border-border bg-card/60 backdrop-blur-sm text-foreground font-semibold text-base hover:bg-accent/10 transition-all flex items-center justify-center gap-2"
              >
                Explore Live Demo (demo@careerbridge.ai)
              </Link>
            </div>

            {/* Metrics Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto p-6 rounded-2xl border border-border bg-card/40 backdrop-blur-md shadow-sm">
              <div>
                <div className="text-3xl font-black text-primary">1,000+</div>
                <div className="text-xs text-muted-foreground font-medium mt-1">Verified Tech Internships</div>
              </div>
              <div>
                <div className="text-3xl font-black text-accent">100%</div>
                <div className="text-xs text-muted-foreground font-medium mt-1">Auditable Explainability</div>
              </div>
              <div>
                <div className="text-3xl font-black text-primary">0%</div>
                <div className="text-xs text-muted-foreground font-medium mt-1">Hallucination Guarantee</div>
              </div>
              <div>
                <div className="text-3xl font-black text-accent">10+</div>
                <div className="text-xs text-muted-foreground font-medium mt-1">Specialized Tech Domains</div>
              </div>
            </div>
          </div>
        </section>

        {/* Employer Brands Bar */}
        <section className="py-12 border-y border-border/40 bg-card/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <p className="text-center text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-8">
              Connecting Students to Opportunities Across Top Tech Leaders
            </p>
            <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-12 opacity-85">
              {EMPLOYER_LOGOS.map((comp) => (
                <div key={comp.name} className="flex items-center gap-2.5 grayscale hover:grayscale-0 transition-all duration-300">
                  <img src={comp.logo} alt={comp.name} className="h-6 sm:h-7 object-contain max-w-[100px]" />
                  <span className="font-semibold text-sm text-foreground/80">{comp.name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Core Features Grid */}
        <section className="py-20 lg:py-28 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">
              Engineered with Agentic Rigor & Absolute Transparency
            </h2>
            <p className="text-muted-foreground text-base sm:text-lg">
              No opaque black-box AI. Every recommendation, resume refinement, and interview evaluation provides complete provenance and factual grounding.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {FEATURES.map((feat) => {
              const Icon = feat.icon;
              return (
                <div
                  key={feat.title}
                  className="p-6 rounded-2xl border border-border/60 bg-card/40 backdrop-blur-sm hover:border-primary/40 hover:bg-card/70 transition-all group"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold mb-2.5 text-foreground">{feat.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feat.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Workflow Showcase */}
        <section className="py-20 bg-card/20 border-t border-border/40">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
            <h2 className="text-3xl font-extrabold tracking-tight mb-12">The 4-Stage Candidate Advantage</h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
              <div className="p-5 rounded-xl border border-border bg-card/50">
                <div className="text-primary font-black text-2xl mb-2">01</div>
                <h4 className="font-bold text-base mb-1.5">Profile & Resume Audit</h4>
                <p className="text-xs text-muted-foreground">Upload your resume to extract skills, action verb density, and instant ATS audit metrics.</p>
              </div>
              <div className="p-5 rounded-xl border border-border bg-card/50">
                <div className="text-primary font-black text-2xl mb-2">02</div>
                <h4 className="font-bold text-base mb-1.5">Hybrid RAG Discovery</h4>
                <p className="text-xs text-muted-foreground">Explore 1,000+ internships with explainable match breakdowns and skill gap roadmaps.</p>
              </div>
              <div className="p-5 rounded-xl border border-border bg-card/50">
                <div className="text-primary font-black text-2xl mb-2">03</div>
                <h4 className="font-bold text-base mb-1.5">Zero-Hallucination Prep</h4>
                <p className="text-xs text-muted-foreground">Generate tailored resumes and cover letters with strict anti-hallucination verification.</p>
              </div>
              <div className="p-5 rounded-xl border border-border bg-card/50">
                <div className="text-primary font-black text-2xl mb-2">04</div>
                <h4 className="font-bold text-base mb-1.5">Voice Mock & Track</h4>
                <p className="text-xs text-muted-foreground">Simulate turn-by-turn voice mock interviews with objective concept coverage scoring.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Banner */}
        <section className="py-16 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-primary/90 via-primary to-accent text-primary-foreground shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <h3 className="text-2xl sm:text-3xl font-black mb-2">Ready to Accelerate Your Career?</h3>
              <p className="text-primary-foreground/80 text-sm sm:text-base max-w-xl">
                Join thousands of students using CareerBridge AI to discover, prepare, and land top software and AI internships.
              </p>
            </div>
            <Link
              to="/register"
              className="px-6 py-3.5 rounded-xl bg-background text-foreground font-bold text-sm hover:bg-background/90 transition-all shrink-0 shadow-lg"
            >
              Create Free Account
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 bg-card/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-bold text-foreground">CareerBridge AI</span> © 2026. All rights reserved.
          </div>
          <div className="flex items-center gap-6">
            <span>FastAPI & Hybrid RAG</span>
            <span>React 18 & TypeScript</span>
            <span>PostgreSQL & pgvector</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
