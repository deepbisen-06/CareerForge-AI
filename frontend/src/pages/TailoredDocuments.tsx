import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileText, Mail, Sparkles, Copy, Check, Download, RefreshCw,
  Loader2, Shield, CheckCircle2, Award, BookmarkCheck, Bookmark
} from 'lucide-react';
import { api } from '../services/api';
import { GeneratedDocument, Internship } from '../types';

export const TailoredDocuments: React.FC = () => {
  const [searchParams] = useSearchParams();
  const internshipIdParam = searchParams.get('internship_id');

  const [internships, setInternships] = useState<Internship[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number>(internshipIdParam ? parseInt(internshipIdParam) : 1);
  const [activeTab, setActiveTab] = useState<'RESUME' | 'COVER_LETTER'>('RESUME');
  const [selectedTone, setSelectedTone] = useState<string>('Professional');

  const [document, setDocument] = useState<GeneratedDocument | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [savedAsVersion, setSavedAsVersion] = useState(false);

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

  const handleGenerate = async (docType: 'TAILORED_RESUME' | 'COVER_LETTER') => {
    if (!selectedJobId) return;
    setIsGenerating(true);
    setSavedAsVersion(false);
    try {
      const doc = await api.documents.generate({
        internship_id: selectedJobId,
        document_type: docType,
        tone: selectedTone
      });
      setDocument(doc);
    } catch (err) {
      console.error("Error generating document:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (selectedJobId) {
      handleGenerate(activeTab === 'RESUME' ? 'TAILORED_RESUME' : 'COVER_LETTER');
    }
  }, [selectedJobId, activeTab, selectedTone]);

  const handleSaveAsVersion = async () => {
    if (!document) return;
    try {
      await api.resume.saveVersion({
        target_internship_id: selectedJobId,
        title: document.title || 'Tailored Version',
        document_type: document.document_type,
        content_markdown: document.content,
        metadata_json: document.metadata
      });
      setSavedAsVersion(true);
    } catch (err) {
      console.error("Error saving resume version:", err);
    }
  };

  const handleCopy = () => {
    if (!document) return;
    navigator.clipboard.writeText(document.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!document) return;
    const blob = new Blob([document.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement('a');
    a.href = url;
    a.download = `${document.title || 'tailored-doc'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Anti-Hallucination Customizer
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">
            Document Customization Studio
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Factual tailored resumes and role-specific cover letters customized for every target internship.
          </p>
        </div>

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
      </div>

      {/* Mode Tabs */}
      <div className="flex items-center justify-between border-b border-border">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('RESUME')}
            className={`pb-3 px-4 text-xs font-bold transition flex items-center gap-2 border-b-2 ${
              activeTab === 'RESUME'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <FileText className="w-4 h-4" /> Tailored ATS Resume
          </button>

          <button
            onClick={() => setActiveTab('COVER_LETTER')}
            className={`pb-3 px-4 text-xs font-bold transition flex items-center gap-2 border-b-2 ${
              activeTab === 'COVER_LETTER'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Mail className="w-4 h-4" /> Role-Specific Cover Letter
          </button>
        </div>

        {/* Cover Letter Tone Selector */}
        {activeTab === 'COVER_LETTER' && (
          <div className="flex items-center gap-2 pb-2">
            <span className="text-xs text-muted-foreground font-semibold">Tone:</span>
            {['Professional', 'Confident', 'Technical', 'Student'].map((t) => (
              <button
                key={t}
                onClick={() => setSelectedTone(t)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${
                  selectedTone === t
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'bg-card text-muted-foreground hover:text-foreground border border-border'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Guardrail Notice */}
      <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-xs flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
          <Shield className="w-4 h-4 shrink-0" />
          <span><strong>Zero-Hallucination Guardrail Active:</strong> Experience, degrees, and projects are strictly reordered and highlighted from verified profile data without fabrication.</span>
        </div>
      </div>

      {/* Document Viewer Container */}
      <div className="p-6 sm:p-8 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-6">
        {/* Document Action Toolbar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border">
          <div>
            <h3 className="font-bold text-base text-foreground">{document?.title || 'Generating Document...'}</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Optimized for ATS parsers and hiring committee screening
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleGenerate(activeTab === 'RESUME' ? 'TAILORED_RESUME' : 'COVER_LETTER')}
              disabled={isGenerating}
              className="p-2 rounded-xl text-xs font-semibold bg-secondary text-secondary-foreground hover:bg-accent transition border border-border"
              title="Regenerate"
            >
              <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
            </button>

            <button
              onClick={handleSaveAsVersion}
              disabled={!document || isGenerating || savedAsVersion}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 border border-border ${
                savedAsVersion ? 'bg-emerald-500/15 text-emerald-600 border-emerald-500/30' : 'bg-secondary text-secondary-foreground hover:bg-accent'
              }`}
            >
              {savedAsVersion ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Bookmark className="w-3.5 h-3.5" />}
              {savedAsVersion ? 'Version Saved' : 'Save Version'}
            </button>

            <button
              onClick={handleCopy}
              disabled={!document || isGenerating}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-secondary text-secondary-foreground hover:bg-accent transition flex items-center gap-1.5 border border-border"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy Text'}
            </button>

            <button
              onClick={handleDownload}
              disabled={!document || isGenerating}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center gap-1.5 shadow-md shadow-primary/20"
            >
              <Download className="w-3.5 h-3.5" /> Export Markdown
            </button>
          </div>
        </div>

        {/* Content Box */}
        {isGenerating ? (
          <div className="py-24 text-center space-y-3">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
            <p className="text-xs text-muted-foreground">Reordering projects and synthesizing tailored phrasing...</p>
          </div>
        ) : (
          <div className="p-6 rounded-2xl bg-background border border-border/70 font-mono text-xs leading-relaxed whitespace-pre-wrap select-text overflow-x-auto text-foreground">
            {document?.content}
          </div>
        )}
      </div>
    </div>
  );
};

export default TailoredDocuments;
