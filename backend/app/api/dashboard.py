from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import User, Resume, Application, SavedJob, SkillGap, Internship, Notification, InterviewSession
from app.schemas.schemas import DashboardOverviewOut, InternshipOut, SkillGapItem, ApplicationOut, ConversionFunnelOut
from app.auth.deps import get_current_user
from app.api.profile import calculate_completion
from app.api.applications import evaluate_deadline_status
from app.agents.matching_agent import matching_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.rag.vector_store import rag_store

router = APIRouter(prefix="/dashboard", tags=["Main Dashboard"])

@router.get("/overview", response_model=DashboardOverviewOut)
def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_name = current_user.profile.full_name if current_user.profile and current_user.profile.full_name else "Student"
    comp_pct = calculate_completion(current_user)

    # Latest Resume score
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    res_score = latest_resume.resume_score if latest_resume else 0.0

    # Saved Jobs Count
    saved_count = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).count()

    # Applications
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    status_counts = {"SAVED": 0, "PLANNED": 0, "APPLIED": 0, "ASSESSMENT": 0, "INTERVIEW": 0, "OFFER": 0, "SELECTED": 0, "REJECTED": 0}
    for a in apps:
        s = a.status.upper()
        if s in status_counts:
            status_counts[s] += 1
        else:
            status_counts[s] = 1

    # Compute Real Conversion Funnel
    total_pipeline = len(apps) + saved_count
    applied_count = status_counts.get("APPLIED", 0) + status_counts.get("ASSESSMENT", 0) + status_counts.get("INTERVIEW", 0) + status_counts.get("OFFER", 0) + status_counts.get("SELECTED", 0)
    interview_count = status_counts.get("INTERVIEW", 0) + status_counts.get("OFFER", 0) + status_counts.get("SELECTED", 0)
    offer_count = status_counts.get("OFFER", 0) + status_counts.get("SELECTED", 0)

    interview_rate = round((interview_count / applied_count) * 100.0, 1) if applied_count > 0 else 0.0
    offer_rate = round((offer_count / applied_count) * 100.0, 1) if applied_count > 0 else 0.0

    funnel = ConversionFunnelOut(
        saved=saved_count + status_counts.get("SAVED", 0),
        planned=status_counts.get("PLANNED", 0),
        applied=status_counts.get("APPLIED", 0),
        assessment=status_counts.get("ASSESSMENT", 0),
        interview=status_counts.get("INTERVIEW", 0),
        offer=status_counts.get("OFFER", 0),
        selected=status_counts.get("SELECTED", 0),
        rejected=status_counts.get("REJECTED", 0),
        interview_rate_pct=interview_rate,
        offer_rate_pct=offer_rate
    )

    # Upcoming Deadlines
    upcoming_apps = []
    for a in apps:
        if a.deadline:
            dl_status = evaluate_deadline_status(a.deadline)
            upcoming_apps.append(ApplicationOut(
                id=a.id,
                user_id=a.user_id,
                internship_id=a.internship_id,
                status=a.status,
                applied_at=a.applied_at,
                deadline=a.deadline,
                notes=a.notes,
                match_score=a.match_score,
                internship=InternshipOut.from_orm(a.internship),
                created_at=a.created_at,
                updated_at=a.updated_at,
                deadline_status=dl_status
            ))
    upcoming_apps.sort(key=lambda x: x.deadline or "")

    # Top Recommended Internships
    user_skills = [us.skill.name for us in current_user.user_skills]
    user_skills_dicts = [{"name": us.skill.name, "proficiency": us.proficiency} for us in current_user.user_skills]
    search_results = rag_store.search(
        query="Software Engineer Machine Learning Data AI",
        top_k=6,
        candidate_skills=user_skills
    )

    prof_dict = {
        "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
        "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
        "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
        "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
        "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
        "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
    }

    top_recs = []
    for r in search_results:
        doc = r["internship"]
        match_res = matching_agent.compute_match(prof_dict, user_skills, doc)
        top_recs.append(InternshipOut(
            id=doc["id"],
            company=doc["company"],
            title=doc["title"],
            domain=doc.get("domain", "Software Development"),
            description=doc["description"],
            requirements=doc.get("requirements", []),
            preferred_skills=doc.get("preferred_skills", []),
            location=doc["location"],
            work_mode=doc["work_mode"],
            stipend=doc.get("stipend"),
            duration=doc.get("duration"),
            eligibility=doc.get("eligibility"),
            deadline=doc.get("deadline"),
            application_url=doc.get("application_url"),
            source=doc.get("source", "Curated Dataset"),
            source_type=doc.get("source_type", "CURATED"),
            company_logo_url=doc.get("company_logo_url"),
            is_demo=doc.get("is_demo", True),
            created_at=doc.get("created_at", "2026-08-15T00:00:00"),
            match_score=match_res["overall_score"]
        ))
    top_recs.sort(key=lambda x: x.match_score or 0, reverse=True)

    # High Priority Skill Gaps (from top match)
    high_gaps = []
    if top_recs:
        top_job = top_recs[0]
        gap_rep = skill_gap_agent.analyze_gaps(user_skills_dicts, {
            "id": top_job.id, "company": top_job.company, "title": top_job.title,
            "requirements": top_job.requirements, "preferred_skills": top_job.preferred_skills
        })
        high_gaps = [
            SkillGapItem(
                skill=g["skill"],
                current_level=g["current_level"],
                required_level=g["required_level"],
                gap_score=g["gap_score"],
                priority=g["priority"],
                status_tag=g.get("status_tag", "MISSING"),
                recommendation=g["recommendation"],
                estimated_hours=g["estimated_hours"],
                learning_resources=g["learning_resources"]
            )
            for g in gap_rep["gaps"] if g["priority"] == "HIGH"
        ]

    # Latest Interview Session Readiness
    latest_interview = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc()).first()
    interview_readiness = latest_interview.readiness_score if latest_interview else 75.0

    # Unread notifications
    unread_count = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.read == False).count()

    return DashboardOverviewOut(
        user_name=user_name,
        profile_completion=comp_pct,
        resume_score=res_score,
        total_applications=len(apps),
        saved_jobs_count=saved_count,
        status_counts=status_counts,
        funnel_metrics=funnel,
        top_recommendations=top_recs[:3],
        high_priority_gaps=high_gaps[:4],
        upcoming_deadlines=upcoming_apps[:4],
        interview_readiness=interview_readiness,
        notifications_unread=unread_count
    )
