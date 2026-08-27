export interface User {
  id: number;
  email: string;
  role?: string; // "student" | "admin"
  is_active?: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name?: string;
  role?: string;
}

export interface Education {
  id?: number;
  degree: string;
  institution: string;
  field?: string;
  start_year?: number;
  end_year?: number;
  cgpa_or_percentage?: string;
}

export interface Experience {
  id?: number;
  company: string;
  role: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

export interface Project {
  id?: number;
  title: string;
  description?: string;
  technologies: string[];
  project_url?: string;
}

export interface UserSkillItem {
  name: string;
  proficiency?: string;
  category?: string;
}

export interface Profile {
  id: number;
  user_id: number;
  full_name?: string;
  phone?: string;
  location?: string;
  career_objective?: string;
  preferred_domains: string[];
  preferred_locations: string[];
  preferred_work_mode: string;
  preferred_stipend: string;
  preferred_duration: string;
  skills: UserSkillItem[];
  educations: Education[];
  experiences: Experience[];
  projects: Project[];
  completion_percentage: number;
}

export interface ResumeVersion {
  id: number;
  user_id: number;
  original_resume_id?: number;
  target_internship_id?: number;
  version_number: number;
  title: string;
  document_type: string;
  content_markdown: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface ResumeAnalysis {
  id: number;
  file_name: string;
  resume_score: number;
  ats_score: number;
  parsed_data: {
    name?: string;
    email?: string;
    phone?: string;
    links?: string[];
    skills?: string[];
    education?: string[];
    experience?: string[];
    projects?: string[];
    certifications?: string[];
    achievements?: string[];
  };
  strengths: string[];
  weaknesses: string[];
  missing_sections: string[];
  recommendations: string[];
  versions?: ResumeVersion[];
  created_at: string;
}

export interface ProvenanceInfo {
  retrieval_score: number;
  rerank_score: number;
  positive_reasons: string[];
  negative_reasons: string[];
  source_type: string;
  retrieved_at?: string;
}

export interface Internship {
  id: number;
  company: string;
  title: string;
  domain: string;
  description: string;
  requirements: string[];
  preferred_skills: string[];
  location: string;
  work_mode: string;
  stipend?: string;
  duration?: string;
  eligibility?: string;
  deadline?: string;
  application_url?: string;
  source: string;
  source_type?: string;
  company_logo_url?: string;
  is_active?: boolean;
  is_demo: boolean;
  is_saved?: boolean;
  match_score?: number;
  provenance?: ProvenanceInfo;
  created_at: string;
  posted_at?: string;
  last_verified_at?: string;
}

export interface SavedJob {
  id: number;
  user_id: number;
  internship_id: number;
  saved_at: string;
  internship: Internship;
}

export interface ScoreBreakdown {
  skills_score: number;
  experience_score: number;
  projects_score: number;
  education_score: number;
  eligibility_score: number;
  preference_score: number;
  weights: {
    skills: number;
    experience: number;
    projects: number;
    education: number;
    eligibility: number;
    preferences: number;
  };
}

export interface MatchExplanation {
  internship_id: number;
  company: string;
  title: string;
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  matched_skills: string[];
  missing_skills: string[];
  strengths: string[];
  discrepancies?: string[];
  eligibility_status: {
    degree_qualified?: boolean;
    graduation_year_aligned?: boolean;
    work_authorization?: boolean;
  };
  is_eligible?: boolean;
  recommendation: string;
  reasoning: string;
}

export interface LearningResource {
  title: string;
  url: string;
  type: string;
}

export interface SkillGapItem {
  id?: number;
  skill: string;
  current_level: string;
  required_level: string;
  gap_score: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status_tag?: 'MATCHED' | 'PARTIAL' | 'MISSING';
  recommendation: string;
  estimated_hours: number;
  learning_resources: LearningResource[];
}

export interface SkillGapReport {
  internship_id: number;
  company: string;
  title: string;
  overall_readiness: number;
  total_gaps: number;
  high_priority_gaps: number;
  gaps: SkillGapItem[];
  action_plan: string[];
}

export interface GeneratedDocument {
  id: number;
  internship_id: number;
  document_type: 'TAILORED_RESUME' | 'COVER_LETTER';
  title?: string;
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface InterviewQuestion {
  id: number;
  question: string;
  category: string;
  difficulty: string;
  ideal_answer?: string;
  user_answer?: string;
  score?: number;
  feedback?: string;
  expected_concepts?: string[];
  detected_concepts?: string[];
  missing_concepts?: string[];
  evaluation_criteria?: {
    accuracy?: number;
    clarity?: number;
    relevance?: number;
    confidence?: number;
  };
}

export interface InterviewSession {
  id: number;
  internship_id: number;
  role_title?: string;
  score: number;
  readiness_score: number;
  feedback_summary?: string;
  strengths: string[];
  areas_for_improvement: string[];
  category_scores?: Record<string, number>;
  questions: InterviewQuestion[];
  created_at: string;
}

export interface FiveDayPlanTask {
  day: number;
  title: string;
  tasks: string[];
  time_estimate: string;
}

export interface PrepPlan {
  internship_id: number;
  role_title: string;
  company: string;
  five_day_plan: FiveDayPlanTask[];
}

export interface InterviewProgress {
  total_sessions: number;
  average_score: number;
  readiness_trend: Array<{ session_number: number; role_title?: string; score: number; date: string }>;
  category_averages: Record<string, number>;
  recurring_weak_topics: string[];
  recent_sessions: InterviewSession[];
}

export type ApplicationStatus =
  | 'SAVED'
  | 'PLANNED'
  | 'APPLIED'
  | 'ASSESSMENT'
  | 'INTERVIEW'
  | 'OFFER'
  | 'SELECTED'
  | 'REJECTED'
  | 'WITHDRAWN';

export interface Application {
  id: number;
  user_id: number;
  internship_id: number;
  status: ApplicationStatus;
  applied_at?: string;
  deadline?: string;
  notes?: string;
  match_score: number;
  internship: Internship;
  created_at: string;
  updated_at: string;
  deadline_status?: 'Overdue' | 'Urgent' | 'Approaching' | 'Normal';
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  tool_calls: Array<{ tool: string; args: Record<string, any> }>;
  created_at: string;
}

export interface NotificationItem {
  id: number;
  type: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

export interface ConversionFunnel {
  saved: number;
  planned: number;
  applied: number;
  assessment: number;
  interview: number;
  offer: number;
  selected: number;
  rejected: number;
  interview_rate_pct: number;
  offer_rate_pct: number;
}

export interface DashboardOverview {
  user_name: string;
  profile_completion: number;
  resume_score: number;
  total_applications: number;
  saved_jobs_count?: number;
  status_counts: Record<string, number>;
  funnel_metrics?: ConversionFunnel;
  top_recommendations: Internship[];
  high_priority_gaps: SkillGapItem[];
  upcoming_deadlines: Application[];
  interview_readiness: number;
  notifications_unread: number;
}

export interface AdminStats {
  total_users: number;
  total_students: number;
  total_internships: number;
  active_internships: number;
  total_applications: number;
  total_interviews_taken: number;
  rag_indexed_count: number;
  ai_status: string;
}

// --- CareerForge Autonomous Agent Types ---
export interface AgentPlanStep {
  step: number;
  tool: string;
  description: string;
  params: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result_summary?: string;
}

export interface AgentEvent {
  id: number;
  run_id: number;
  event_type: string;
  message: string;
  tool_name?: string;
  structured_data: Record<string, any>;
  created_at: string;
}

export interface AgentOpportunityCard {
  internship_id: number;
  company: string;
  title: string;
  location: string;
  work_mode: string;
  stipend?: string;
  deadline?: string;
  source: string;
  match_score: number;
  factor_breakdown?: Record<string, number>;
  eligibility_status: 'ELIGIBLE' | 'PARTIALLY_ELIGIBLE' | 'NOT_ELIGIBLE' | 'UNKNOWN';
  eligibility_details: string[];
  strengths: string[];
  missing_requirements: string[];
  skill_gap_summary?: string;
  critical_skills?: string[];
  application_url?: string;
}

export interface AgentSummaryPayload {
  executive_summary: string;
  metrics: {
    total_evaluated: number;
    high_confidence_matches: number;
    verified_eligible: number;
  };
  next_actions: string[];
  top_opportunities: AgentOpportunityCard[];
  application_package?: {
    internship_id: number;
    company: string;
    title: string;
    cover_letter_draft: string;
    resume_tailoring: string;
    fact_validation_status: string;
    action_required: string;
    checklist: string[];
  };
}

export interface AgentRun {
  id: number;
  user_id: number;
  goal: string;
  execution_plan: AgentPlanStep[];
  status: 'PENDING' | 'PLANNING' | 'RUNNING' | 'AWAITING_APPROVAL' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  final_summary: AgentSummaryPayload;
  created_at: string;
  completed_at?: string;
  events?: AgentEvent[];
}
