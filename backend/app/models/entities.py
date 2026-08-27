from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False) # "student", "admin"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    recommendation_feedbacks = relationship("RecommendationFeedback", back_populates="user", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    career_objective = Column(Text, nullable=True)
    preferred_domains = Column(JSON, default=list)        # e.g. ["AI/ML", "Data Science", "Software Development"]
    preferred_locations = Column(JSON, default=list)      # e.g. ["Bangalore", "Remote", "Hyderabad"]
    preferred_work_mode = Column(String(50), default="Any") # Remote, Hybrid, Onsite, Any
    preferred_stipend = Column(String(100), default="Any") # e.g. "₹25,000+/month"
    preferred_duration = Column(String(100), default="Any") # e.g. "3-6 months"
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, default=dict) # parsed sections: contact, skills, education, experience, projects, etc.
    resume_score = Column(Float, default=0.0) # ATS overall score 0-100
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    missing_sections = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="original_resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    target_internship_id = Column(Integer, ForeignKey("internships.id", ondelete="SET NULL"), nullable=True)
    version_number = Column(Integer, default=1, nullable=False)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), default="TAILORED_RESUME") # "TAILORED_RESUME", "COVER_LETTER", "OPTIMIZED_BASE"
    content_markdown = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict) # model, fact_validation_status, highlighted_skills
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="resume_versions")
    original_resume = relationship("Resume", back_populates="versions")
    target_internship = relationship("Internship")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), index=True, default="General") # Programming, AI/ML, Cloud/DevOps, Web, Data, etc.

    user_skills = relationship("UserSkill", back_populates="skill")
    internship_skills = relationship("InternshipSkill", back_populates="skill")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(String(50), default="Intermediate") # Beginner, Intermediate, Advanced, Expert
    source = Column(String(50), default="profile")           # resume, profile, assessment

    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    field = Column(String(255), nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    cgpa_or_percentage = Column(String(50), nullable=True)

    user = relationship("User", back_populates="educations")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)

    user = relationship("User", back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    project_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="projects")


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    location = Column(String(255), index=True, nullable=False)
    work_mode = Column(String(50), index=True, default="Remote") # Remote, Hybrid, Onsite
    stipend = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    eligibility = Column(String(255), nullable=True)
    deadline = Column(String(50), nullable=True)
    application_url = Column(String(500), nullable=True)
    domain = Column(String(100), index=True, default="Software Development")
    source = Column(String(100), default="Curated Dataset")
    source_type = Column(String(50), default="CURATED") # CURATED, LIVE, DEMO
    source_url = Column(String(500), nullable=True)
    source_job_id = Column(String(255), nullable=True, index=True)
    company_logo_url = Column(String(500), nullable=True)
    posted_at = Column(DateTime, default=utc_now)
    last_verified_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    internship_skills = relationship("InternshipSkill", back_populates="internship", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="internship", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedJob", back_populates="internship", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="internship", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="internship", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="internship", cascade="all, delete-orphan")
    recommendation_feedbacks = relationship("RecommendationFeedback", back_populates="internship", cascade="all, delete-orphan")


class InternshipSkill(Base):
    __tablename__ = "internship_skills"

    id = Column(Integer, primary_key=True, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required = Column(Boolean, default=True)
    importance = Column(Float, default=1.0)

    internship = relationship("Internship", back_populates="internship_skills")
    skill = relationship("Skill", back_populates="internship_skills")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="saved_jobs")
    internship = relationship("Internship", back_populates="saved_by_users")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), index=True, default="SAVED") # SAVED, PLANNED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, SELECTED, REJECTED, WITHDRAWN
    applied_at = Column(DateTime, nullable=True)
    deadline = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    match_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    skill = Column(String(100), nullable=False)
    current_level = Column(String(50), default="None")    # None, Beginner, Intermediate
    required_level = Column(String(50), default="Intermediate") # Intermediate, Advanced
    gap_score = Column(Float, default=1.0)
    priority = Column(String(20), default="MEDIUM")       # HIGH, MEDIUM, LOW
    status_tag = Column(String(20), default="MISSING")    # MATCHED, PARTIAL, MISSING
    recommendation = Column(Text, nullable=True)
    estimated_hours = Column(Integer, default=10)
    learning_resources = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="skill_gaps")
    internship = relationship("Internship", back_populates="skill_gaps")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False) # TAILORED_RESUME, COVER_LETTER
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="generated_documents")
    internship = relationship("Internship", back_populates="generated_documents")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    role_title = Column(String(255), nullable=True)
    score = Column(Float, default=0.0)
    readiness_score = Column(Float, default=0.0) # 0-100%
    feedback_summary = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)
    category_scores = Column(JSON, default=dict) # technical, behavioral, communication, confidence
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="interview_sessions")
    internship = relationship("Internship", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String(50), default="Technical") # Technical, HR, Behavioral, Resume-based, Role-specific
    difficulty = Column(String(50), default="Medium")  # Easy, Medium, Hard
    ideal_answer = Column(Text, nullable=True)
    user_answer = Column(Text, nullable=True)
    score = Column(Float, nullable=True)               # 0-10
    feedback = Column(Text, nullable=True)
    expected_concepts = Column(JSON, default=list)     # ["concept1", "concept2"]
    detected_concepts = Column(JSON, default=list)     # ["concept1"]
    missing_concepts = Column(JSON, default=list)      # ["concept2"]
    evaluation_criteria = Column(JSON, default=dict)   # accuracy, clarity, relevance, confidence

    session = relationship("InterviewSession", back_populates="questions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="Career Assistant Chat")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="messages")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), default="DEADLINE") # DEADLINE, MATCH, INTERVIEW, SYSTEM
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    scheduled_for = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="notifications")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    is_positive = Column(Boolean, nullable=False) # True = Useful, False = Not Useful
    reason_category = Column(String(100), nullable=True) # "too_difficult", "wrong_domain", "location_mismatch", "already_applied", "not_interested"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="recommendation_feedbacks")
    internship = relationship("Internship", back_populates="recommendation_feedbacks")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal = Column(Text, nullable=False)
    execution_plan = Column(JSON, default=list) # List of steps with status & tool info
    status = Column(String(50), index=True, default="PENDING") # PENDING, PLANNING, RUNNING, AWAITING_APPROVAL, COMPLETED, FAILED, CANCELLED
    final_summary = Column(JSON, default=dict) # High-impact metrics, top recommendations, action items
    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="agent_runs")
    events = relationship("AgentEvent", back_populates="run", cascade="all, delete-orphan")


class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False) # plan_created, tool_selected, tool_completed, eligibility_checked, etc.
    message = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=True)
    structured_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    run = relationship("AgentRun", back_populates="events")

