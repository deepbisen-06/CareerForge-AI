import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud, FileText, CheckCircle2, AlertTriangle, Sparkles,
  Download, RefreshCw, Loader2, Check, ArrowRight, Shield, Award,
  Clock, History, Trash2
} from 'lucide-react';
import { api } from '../services/api';
import { ResumeAnalysis, ResumeVersion } from '../types';

export const ResumeStudio: React.FC = () => {
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumeData = async () => {
    try {
      const [latest, verList] = await Promise.all([
        api.resume.getLatest(),
        api.resume.getVersions()
      ]);
      setAnalysis(latest);
      setVersions(verList);
    } catch {
      // No resume yet
    }
  };

  useEffect(() => {
    fetchResumeData();
  }, []);

  const handleFileUpload = async (file: File) => {
    setError('');
    setIsUploading(true);
    setUploadStep('Extracting text from document...');

    try {
      await new Promise(r => setTimeout(r, 400));
      setUploadStep('Parsing sections and extracting technical skills...');
      await new Promise(r => setTimeout(r, 400));
      setUploadStep('Running ATS scoring algorithm & intelligence audit...');

      const formData = new FormData();
      formData.append('file', file);
      const result = await api.resume.upload(formData);
      setAnalysis(result);
      await fetchResumeData();
    } catch (err: any) {
      setError(err.message || 'Failed to upload and parse resume');
    } finally {
      setIsUploading(false);
      setUploadStep('');
    }
  };

  const handleDeleteVersion = async (versionId: number) => {
    try {
      await api.resume.deleteVersion(versionId);
      setVersions(prev => prev.filter(v => v.id !== versionId));
    } catch {
      // ignore
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="border-b border-border/60 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Shield className="w-3.5 h-3.5" /> ATS 2.0 Audit & Version Engine
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Resume Intelligence Studio</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Upload your master resume in PDF or DOCX format for instant ATS scoring, skill extraction, and version tracking.
          </p>
        </div>

        <button
          onClick={() => navigate('/documents')}
          className="px-4 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 transition shadow-md shadow-primary/20 flex items-center gap-2 self-start"
        >
          <Sparkles className="w-4 h-4" /> Tailor for Specific Job
        </button>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className="p-8 sm:p-10 rounded-3xl border-2 border-dashed border-border hover:border-primary/50 bg-card/40 backdrop-blur-sm transition-all text-center space-y-4 relative"
      >
        <input
          type="file"
          ref={fileInputRef}
          accept=".pdf,.docx,.doc,.txt"
          className="hidden"
          onChange={(e) => e.target.files && e.target.files[0] && handleFileUpload(e.target.files[0])}
        />

        <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto shadow-sm">
          <UploadCloud className="w-7 h-7" />
        </div>

        <div>
          <h3 className="text-base font-bold text-foreground">Upload Master Resume Document</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Drag and drop your PDF or DOCX here, or click to browse (Max 5MB)
          </p>
        </div>

        {isUploading ? (
          <div className="p-4 rounded-2xl bg-muted/60 border border-border inline-flex items-center gap-3">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
            <span className="text-xs font-semibold text-primary">{uploadStep}</span>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-6 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition shadow-md shadow-primary/20"
          >
            Select Resume File
          </button>
        )}

        {error && (
          <p className="text-xs text-destructive font-medium mt-2">{error}</p>
        )}
      </div>

      {/* Analysis Results Display */}
      {analysis && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Top Score Banner */}
          <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-500 flex flex-col items-center justify-center text-white font-black shadow-lg shadow-emerald-500/20 shrink-0">
                <span className="text-2xl leading-none">{analysis.ats_score}</span>
                <span className="text-[10px] font-semibold opacity-90">ATS Score</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-foreground">{analysis.file_name}</h2>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    High ATS Compatibility
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Parsed on {new Date(analysis.created_at).toLocaleDateString()} • {analysis.parsed_data.skills?.length || 0} skills extracted
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-secondary text-secondary-foreground hover:bg-accent transition flex items-center gap-1.5 border border-border"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Re-upload
              </button>
            </div>
          </div>

          {/* Detailed Strengths & Recommendations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-3">
              <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Identified ATS Strengths</span>
              </div>
              <div className="space-y-2">
                {analysis.strengths.map((s, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/15 text-xs text-foreground flex items-start gap-2">
                    <span className="text-emerald-500 font-bold">✓</span>
                    <span className="leading-relaxed">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-3">
              <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>Actionable ATS Improvements</span>
              </div>
              <div className="space-y-2">
                {analysis.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-amber-500/5 border border-amber-500/15 text-xs text-foreground flex items-start gap-2">
                    <span className="text-amber-500 font-bold">💡</span>
                    <span className="leading-relaxed">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Extracted Skills Section */}
          <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-4">
            <h3 className="text-sm font-bold flex items-center gap-2 text-foreground">
              <Award className="w-4 h-4 text-primary" />
              Extracted Technical Skills & Keywords ({analysis.parsed_data.skills?.length || 0})
            </h3>
            <div className="flex flex-wrap gap-2">
              {analysis.parsed_data.skills?.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-xl bg-primary/10 text-primary border border-primary/20 text-xs font-semibold"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Resume Version History Section */}
          <div className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold flex items-center gap-2 text-foreground">
                <History className="w-4 h-4 text-accent" />
                Resume Version History ({versions.length})
              </h3>
            </div>

            {versions.length === 0 ? (
              <p className="text-xs text-muted-foreground">No tailored resume versions saved yet.</p>
            ) : (
              <div className="divide-y divide-border/60">
                {versions.map((ver) => (
                  <div key={ver.id} className="py-3 flex items-center justify-between gap-4">
                    <div>
                      <div className="font-semibold text-xs text-foreground flex items-center gap-2">
                        <span>v{ver.version_number}: {ver.title}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-muted text-muted-foreground">
                          {ver.document_type}
                        </span>
                      </div>
                      <div className="text-[11px] text-muted-foreground mt-0.5">
                        Saved on {new Date(ver.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <button
                      onClick={() => handleDeleteVersion(ver.id)}
                      className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition"
                      title="Delete version"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeStudio;
