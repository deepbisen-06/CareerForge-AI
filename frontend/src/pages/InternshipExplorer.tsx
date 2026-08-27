import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Filter, MapPin, Briefcase, DollarSign, Clock, Sparkles,
  ChevronRight, Bookmark, Check, Loader2, BookmarkCheck, ThumbsUp, ThumbsDown
} from 'lucide-react';
import { api } from '../services/api';
import { Internship } from '../types';

export const InternshipExplorer: React.FC = () => {
  const navigate = useNavigate();
  const [internships, setInternships] = useState<Internship[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [selectedWorkMode, setSelectedWorkMode] = useState('All');
  const [selectedSourceType, setSelectedSourceType] = useState('All');

  const domains = [
    'All', 'AI/ML', 'Data Science', 'Software Development', 'Fullstack Development',
    'Frontend Development', 'Cloud & DevOps', 'Cybersecurity', 'Mobile Development',
    'Robotics & IoT', 'Product Management'
  ];

  const fetchInternships = async () => {
    setIsLoading(true);
    try {
      const data = await api.internships.list({
        q: searchQuery || undefined,
        domain: selectedDomain === 'All' ? undefined : selectedDomain,
        work_mode: selectedWorkMode === 'All' ? undefined : selectedWorkMode,
        source_type: selectedSourceType === 'All' ? undefined : selectedSourceType,
        limit: 100
      });
      setInternships(data);
    } catch (err) {
      console.error("Error searching internships:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchInternships();
    }, 300);
    return () => clearTimeout(delayDebounce);
  }, [searchQuery, selectedDomain, selectedWorkMode, selectedSourceType]);

  const handleToggleSave = async (job: Internship, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      if (job.is_saved) {
        await api.internships.unsave(job.id);
        setInternships(prev => prev.map(j => j.id === job.id ? { ...j, is_saved: false } : j));
      } else {
        await api.internships.save(job.id);
        setInternships(prev => prev.map(j => j.id === job.id ? { ...j, is_saved: true } : j));
      }
    } catch (err) {
      console.error("Error toggling saved state:", err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-fadeIn">
      {/* Header & Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Hybrid RAG Semantic Retrieval Engine
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">
            Internship Explorer & Recommendation Engine
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Search 1,000+ verified tech opportunities with instant multi-factor compatibility scoring and provenance reasoning.
          </p>
        </div>
      </div>

      {/* Search & Filter Controls Bar */}
      <div className="p-4 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Semantic Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by role, skills, company (e.g. 'FastAPI and PyTorch backend' or 'Remote React')..."
              className="w-full bg-background border border-input rounded-2xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>

          {/* Domain Filter Dropdown */}
          <div className="flex flex-wrap gap-2">
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-background border border-input rounded-2xl px-3.5 py-2.5 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              {domains.map(d => (
                <option key={d} value={d}>Domain: {d}</option>
              ))}
            </select>

            {/* Work Mode Filter Dropdown */}
            <select
              value={selectedWorkMode}
              onChange={(e) => setSelectedWorkMode(e.target.value)}
              className="bg-background border border-input rounded-2xl px-3.5 py-2.5 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              <option value="All">Mode: All</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Onsite">Onsite</option>
            </select>

            {/* Source Type Filter Dropdown */}
            <select
              value={selectedSourceType}
              onChange={(e) => setSelectedSourceType(e.target.value)}
              className="bg-background border border-input rounded-2xl px-3.5 py-2.5 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              <option value="All">Source: All</option>
              <option value="CURATED">Curated Verified</option>
              <option value="LIVE">Live Feed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Internships Grid List */}
      {isLoading ? (
        <div className="py-16 text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
          <p className="text-xs text-muted-foreground">Running Hybrid RAG semantic search & candidate scoring...</p>
        </div>
      ) : internships.length === 0 ? (
        <div className="py-16 text-center rounded-3xl bg-card border border-border space-y-3">
          <p className="text-sm font-semibold">No internships found matching your search criteria.</p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedDomain('All'); setSelectedWorkMode('All'); setSelectedSourceType('All'); }}
            className="text-xs text-primary font-medium hover:underline"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {internships.map((job) => {
            return (
              <div
                key={job.id}
                onClick={() => navigate(`/internships/${job.id}`)}
                className="p-6 rounded-3xl bg-card/60 backdrop-blur-sm border border-border/80 hover:border-primary/50 transition-all cursor-pointer shadow-sm hover:shadow-lg flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  {/* Top Meta */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      {job.company_logo_url ? (
                        <img
                          src={job.company_logo_url}
                          alt=""
                          className="w-10 h-10 object-contain rounded-xl p-1 bg-muted/40 shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0">
                          {job.company[0]}
                        </div>
                      )}
                      <div>
                        <span className="text-[11px] font-bold text-primary">
                          {job.company}
                        </span>
                        <h3 className="font-bold text-base text-foreground group-hover:text-primary transition line-clamp-1">
                          {job.title}
                        </h3>
                      </div>
                    </div>

                    <div className="px-2.5 py-1 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-extrabold text-xs shrink-0">
                      {job.match_score || 85}% Match
                    </div>
                  </div>

                  {/* Details */}
                  <div className="space-y-1.5 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{job.location} ({job.work_mode})</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <DollarSign className="w-3.5 h-3.5 shrink-0" />
                      <span className="font-medium text-foreground">{job.stipend || 'Competitive'}</span>
                    </div>
                  </div>

                  {/* Provenance Reasons if from RAG */}
                  {job.provenance?.positive_reasons && job.provenance.positive_reasons.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-primary/5 border border-primary/15 text-[11px] text-muted-foreground line-clamp-2">
                      <span className="font-semibold text-primary">Why: </span>
                      {job.provenance.positive_reasons[0]}
                    </div>
                  )}

                  {/* Skill Chips */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {job.requirements.slice(0, 3).map((req, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-secondary text-secondary-foreground"
                      >
                        {req}
                      </span>
                    ))}
                    {job.requirements.length > 3 && (
                      <span className="px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        +{job.requirements.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Action Buttons */}
                <div className="pt-3 border-t border-border/60 flex items-center justify-between">
                  <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {job.deadline || 'Upcoming'}
                  </span>

                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={(e) => handleToggleSave(job, e)}
                      className={`p-2 rounded-xl border transition ${
                        job.is_saved
                          ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                          : 'hover:bg-accent text-muted-foreground border-border'
                      }`}
                      title={job.is_saved ? 'Bookmarked' : 'Bookmark'}
                    >
                      <Bookmark className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/internships/${job.id}`);
                      }}
                      className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center gap-1 shadow-md shadow-primary/20"
                    >
                      View Details <ChevronRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default InternshipExplorer;
