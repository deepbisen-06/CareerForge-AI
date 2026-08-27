import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { SavedJob } from '../types';
import {
  Bookmark,
  BookmarkX,
  Building2,
  MapPin,
  Clock,
  ArrowRight,
  Briefcase,
  Layers,
  Sparkles,
  ExternalLink
} from 'lucide-react';

export const SavedJobs: React.FC = () => {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);

  const fetchSaved = async () => {
    try {
      setIsLoading(true);
      const data = await api.internships.getSaved();
      setSavedJobs(data);
    } catch (err: any) {
      setFeedback(err.message || 'Failed to load saved jobs');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (internshipId: number) => {
    try {
      await api.internships.unsave(internshipId);
      setSavedJobs((prev) => prev.filter((s) => s.internship_id !== internshipId));
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="border-b border-border/60 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <Bookmark className="w-3.5 h-3.5" /> Bookmarked Opportunities
          </div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Saved Internships</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Keep track of target roles you plan to customize resumes for and submit applications.
          </p>
        </div>

        <Link
          to="/internships"
          className="px-4 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 transition shadow-md shadow-primary/20 flex items-center gap-2 self-start"
        >
          <Briefcase className="w-4 h-4" /> Explore More Roles
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">Loading your bookmarked internships...</p>
        </div>
      ) : savedJobs.length === 0 ? (
        <div className="text-center py-16 p-8 border border-dashed border-border rounded-2xl bg-card/40">
          <Bookmark className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
          <h3 className="text-lg font-bold text-foreground mb-1">No Saved Internships Yet</h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto mb-6">
            Bookmark high-compatibility internships in the Explorer to track and prepare custom documents for them here.
          </p>
          <Link
            to="/internships"
            className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 transition shadow-md shadow-primary/20 inline-flex items-center gap-2"
          >
            Explore Internships <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedJobs.map((item) => {
            const job = item.internship;
            return (
              <div
                key={item.id}
                className="p-6 rounded-2xl border border-border/70 bg-card/60 backdrop-blur-sm hover:border-primary/40 hover:shadow-lg transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div className="flex items-center gap-3">
                      {job.company_logo_url ? (
                        <img
                          src={job.company_logo_url}
                          alt=""
                          className="w-10 h-10 object-contain rounded-lg p-1 bg-muted/40 shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0">
                          {job.company[0]}
                        </div>
                      )}
                      <div>
                        <h3 className="font-bold text-base text-foreground leading-snug group-hover:text-primary transition-colors">
                          {job.title}
                        </h3>
                        <p className="text-xs text-muted-foreground font-medium">{job.company}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => handleUnsave(job.id)}
                      className="p-2 rounded-lg text-rose-500 hover:bg-rose-500/10 transition shrink-0"
                      title="Remove from saved"
                    >
                      <BookmarkX className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2 text-xs text-muted-foreground mb-4">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5" /> {job.location}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" /> {job.work_mode}
                    </span>
                  </div>

                  {job.match_score !== undefined && (
                    <div className="p-2.5 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-between mb-4">
                      <span className="text-xs font-semibold text-foreground">AI Compatibility</span>
                      <span className="text-xs font-black text-primary">{job.match_score}%</span>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-1.5 mb-6">
                    {job.requirements.slice(0, 3).map((r) => (
                      <span
                        key={r}
                        className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-muted/60 text-muted-foreground"
                      >
                        {r}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-border/60 flex items-center justify-between gap-2">
                  <Link
                    to={`/internships/${job.id}`}
                    className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                  >
                    View Details <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                  <Link
                    to={`/documents?internship_id=${job.id}`}
                    className="px-3 py-1.5 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 text-xs font-semibold transition"
                  >
                    Tailor Resume
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SavedJobs;
