from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth & User ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = "Student"
    role: Optional[str] = "student" # "student" or "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: Optional[str] = None
    role: str = "student"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str = "student"
    is_active: bool = True
    created_at: datetime
    class Config:
        from_attributes = True

# --- Profile ---
class EducationSchema(BaseModel):
    id: Optional[int] = None
    degree: str
    institution: str
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    cgpa_or_percentage: Optional[str] = None

class ExperienceSchema(BaseModel):
    id: Optional[int] = None
    company: str
    role: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    project_url: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    career_objective: Optional[str] = None
    preferred_domains: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_work_mode: Optional[str] = None
    preferred_stipend: Optional[str] = None
    preferred_duration: Optional[str] = None
    skills: Optional[List[Dict[str, Any]]] = None # [{"name": "Python", "proficiency": "Advanced"}]
    educations: Optional[List[EducationSchema]] = None
    experiences: Optional[List[ExperienceSchema]] = None
    projects: Optional[List[ProjectSchema]] = None

class ProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    career_objective: Optional[str] = None
    preferred_domains: List[str] = []
    preferred_locations: List[str] = []
    preferred_work_mode: str = "Any"
    preferred_stipend: str = "Any"
    preferred_duration: str = "Any"
    skills: List[Dict[str, Any]] = []
    educations: List[EducationSchema] = []
    experiences: List[ExperienceSchema] = []
    projects: List[ProjectSchema] = []
    completion_percentage: int = 0
    class Config:
        from_attributes = True

# --- Resume & Versions ---
class ResumeVersionCreate(BaseModel):
    target_internship_id: Optional[int] = None
    title: str
    document_type: str = "TAILORED_RESUME"
    content_markdown: str
    metadata_json: Optional[Dict[str, Any]] = {}

class ResumeVersionOut(BaseModel):
    id: int
    user_id: int
    original_resume_id: Optional[int] = None
    target_internship_id: Optional[int] = None
    version_number: int
    title: str
    document_type: str
    content_markdown: str
    metadata_json: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ResumeAnalysisOut(BaseModel):
    id: int
    file_name: str
    resume_score: float
    ats_score: float
    parsed_data: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    missing_sections: List[str]
    recommendations: List[str]
    versions: List[ResumeVersionOut] = []
    created_at: datetime
    class Config:
        from_attributes = True

# --- Internship & Ingestion ---
class InternshipBase(BaseModel):
    company: str
    title: str
    description: str
    requirements: List[str] = []
    preferred_skills: List[str] = []
    location: str
    work_mode: str = "Remote"
    stipend: Optional[str] = None
    duration: Optional[str] = None
    eligibility: Optional[str] = None
    deadline: Optional[str] = None
    application_url: Optional[str] = None
    domain: str = "Software Development"
    source: str = "Curated Dataset"
    source_type: str = "CURATED" # CURATED, LIVE, DEMO
    source_url: Optional[str] = None
    source_job_id: Optional[str] = None
    company_logo_url: Optional[str] = None
    is_active: bool = True
    is_demo: bool = True

class InternshipCreate(InternshipBase):
    pass

class InternshipUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    stipend: Optional[str] = None
    duration: Optional[str] = None
    eligibility: Optional[str] = None
    deadline: Optional[str] = None
    application_url: Optional[str] = None
    domain: Optional[str] = None
    company_logo_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProvenanceInfo(BaseModel):
    retrieval_score: float = 0.0
    rerank_score: float = 0.0
    positive_reasons: List[str] = []
    negative_reasons: List[str] = []
    source_type: str = "CURATED"
    retrieved_at: Optional[datetime] = None

class InternshipOut(InternshipBase):
    id: int
    created_at: datetime
    posted_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    is_saved: Optional[bool] = False
    match_score: Optional[float] = None
    provenance: Optional[ProvenanceInfo] = None
    class Config:
        from_attributes = True

# --- Saved Job ---
class SavedJobOut(BaseModel):
    id: int
    user_id: int
    internship_id: int
    saved_at: datetime
    internship: InternshipOut
    class Config:
        from_attributes = True

# --- Matching & Explainability ---
class ScoreBreakdown(BaseModel):
    skills_score: float
    experience_score: float
    projects_score: float
    education_score: float
    eligibility_score: float
    preference_score: float
    weights: Dict[str, float]

class MatchExplanationOut(BaseModel):
    internship_id: int
    company: str
    title: str
    overall_score: float # 0-100%
    score_breakdown: ScoreBreakdown
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    discrepancies: List[str] = []
    eligibility_status: Dict[str, Any]
    is_eligible: bool = True
    recommendation: str
    reasoning: str

class RecommendationFeedbackIn(BaseModel):
    internship_id: int
    is_positive: bool
    reason_category: Optional[str] = None # "too_difficult", "wrong_domain", "location_mismatch", "already_applied", "not_interested"
    notes: Optional[str] = None

# --- Skill Gap ---
class SkillGapItem(BaseModel):
    id: Optional[int] = None
    skill: str
    current_level: str
    required_level: str
    gap_score: float
    priority: str # HIGH, MEDIUM, LOW
    status_tag: str = "MISSING" # MATCHED, PARTIAL, MISSING
    recommendation: str
    estimated_hours: int
    learning_resources: List[Dict[str, str]]

class SkillGapReportOut(BaseModel):
    internship_id: int
    company: str
    title: str
    overall_readiness: float
    total_gaps: int
    high_priority_gaps: int
    gaps: List[SkillGapItem]
    action_plan: List[str]

# --- Documents ---
class GenerateDocumentRequest(BaseModel):
    internship_id: int
    document_type: str = "TAILORED_RESUME" # or "COVER_LETTER"
    tone: Optional[str] = "Professional"   # Professional, Confident, Technical, Student
    additional_notes: Optional[str] = None

class GeneratedDocumentOut(BaseModel):
    id: int
    internship_id: int
    document_type: str
    title: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    class Config:
        from_attributes = True

# --- Interview ---
class GenerateQuestionsRequest(BaseModel):
    internship_id: int
    categories: Optional[List[str]] = None # Technical, Behavioral, HR, Resume-based, Role-specific
    count: int = 8

class InterviewQuestionOut(BaseModel):
    id: int
    question: str
    category: str
    difficulty: str
    ideal_answer: Optional[str] = None
    user_answer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    expected_concepts: List[str] = []
    detected_concepts: List[str] = []
    missing_concepts: List[str] = []
    evaluation_criteria: Dict[str, Any] = {}

class InterviewSessionOut(BaseModel):
    id: int
    internship_id: int
    role_title: Optional[str] = None
    score: float
    readiness_score: float
    feedback_summary: Optional[str] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    category_scores: Dict[str, float] = {}
    questions: List[InterviewQuestionOut] = []
    created_at: datetime
    class Config:
        from_attributes = True

class SubmitAnswerRequest(BaseModel):
    question_id: int
    user_answer: str

class PrepPlanOut(BaseModel):
    internship_id: int
    role_title: str
    company: str
    five_day_plan: List[Dict[str, Any]] # [{"day": 1, "title": "...", "tasks": [...]}]

class InterviewProgressOut(BaseModel):
    total_sessions: int
    average_score: float
    readiness_trend: List[Dict[str, Any]] # [{"date": "...", "score": 82.0}]
    category_averages: Dict[str, float]   # {"Technical": 8.5, "Behavioral": 8.0, "HR": 9.0}
    recurring_weak_topics: List[str]
    recent_sessions: List[InterviewSessionOut]

# --- Applications ---
class ApplicationCreate(BaseModel):
    internship_id: int
    status: str = "SAVED" # SAVED, PLANNED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, SELECTED, REJECTED, WITHDRAWN
    deadline: Optional[str] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    user_id: int
    internship_id: int
    status: str
    applied_at: Optional[datetime] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None
    match_score: float
    internship: InternshipOut
    created_at: datetime
    updated_at: datetime
    deadline_status: Optional[str] = "Normal" # "Overdue", "Urgent", "Approaching", "Normal"
    class Config:
        from_attributes = True

# --- Chat Assistant ---
class ChatMessageIn(BaseModel):
    session_id: Optional[int] = None
    message: str

class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    tool_calls: List[Dict[str, Any]] = []
    created_at: datetime

class ChatSessionOut(BaseModel):
    id: int
    title: str
    messages: List[ChatMessageOut] = []
    created_at: datetime
    updated_at: datetime

# --- Notifications ---
class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# --- Dashboard & Analytics ---
class ConversionFunnelOut(BaseModel):
    saved: int
    planned: int
    applied: int
    assessment: int
    interview: int
    offer: int
    selected: int
    rejected: int
    interview_rate_pct: float
    offer_rate_pct: float

class DashboardOverviewOut(BaseModel):
    user_name: str
    profile_completion: int
    resume_score: float
    total_applications: int
    saved_jobs_count: int = 0
    status_counts: Dict[str, int]
    funnel_metrics: Optional[ConversionFunnelOut] = None
    top_recommendations: List[InternshipOut]
    high_priority_gaps: List[SkillGapItem]
    upcoming_deadlines: List[ApplicationOut]
    interview_readiness: float
    notifications_unread: int

# --- Admin Schemas ---
class AdminStatsOut(BaseModel):
    total_users: int
    total_students: int
    total_internships: int
    active_internships: int
    total_applications: int
    total_interviews_taken: int
    rag_indexed_count: int
    ai_status: str = "online"

class IngestionRequestIn(BaseModel):
    source_name: str = "Curated Dataset"
    refresh_vectors: bool = True
    limit: Optional[int] = 1000
