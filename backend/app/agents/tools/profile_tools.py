from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entities import User, Profile, UserSkill, Education, Experience, Project, Resume

def analyze_candidate_profile(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Extracts structured candidate profile data including skills, education,
    experience, projects, and latest resume parsing. Identifies missing fields.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": f"User {user_id} not found", "is_sufficient": False}

    profile = user.profile
    profile_data = {
        "full_name": profile.full_name if profile else "Candidate",
        "email": user.email,
        "phone": profile.phone if profile else None,
        "location": profile.location if profile else None,
        "career_objective": profile.career_objective if profile else None,
        "preferred_domains": profile.preferred_domains if profile and profile.preferred_domains else ["Software Development"],
        "preferred_locations": profile.preferred_locations if profile and profile.preferred_locations else ["Remote"],
        "preferred_work_mode": profile.preferred_work_mode if profile else "Any",
    }

    # Skills
    skills_list = []
    for us in user.user_skills:
        if us.skill:
            skills_list.append({
                "name": us.skill.name,
                "proficiency": us.proficiency or "Intermediate",
                "category": us.skill.category or "General"
            })

    # Education
    educations = []
    for edu in user.educations:
        educations.append({
            "degree": edu.degree,
            "institution": edu.institution,
            "field": edu.field,
            "start_year": edu.start_year,
            "end_year": edu.end_year,
            "cgpa": edu.cgpa_or_percentage
        })

    # Experience
    experiences = []
    for exp in user.experiences:
        experiences.append({
            "company": exp.company,
            "role": exp.role,
            "description": exp.description,
            "start_date": exp.start_date,
            "end_date": exp.end_date
        })

    # Projects
    projects = []
    for proj in user.projects:
        projects.append({
            "title": proj.title,
            "description": proj.description,
            "technologies": proj.technologies or [],
            "project_url": proj.project_url
        })

    # Latest Resume
    latest_resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
    resume_info = None
    if latest_resume:
        resume_info = {
            "id": latest_resume.id,
            "score": latest_resume.resume_score,
            "strengths": latest_resume.strengths or [],
            "weaknesses": latest_resume.weaknesses or [],
            "parsed_data": latest_resume.parsed_data or {}
        }
        # Supplement skills if user_skills was empty
        if not skills_list and latest_resume.parsed_data:
            for s in latest_resume.parsed_data.get("skills", []):
                skills_list.append({"name": s, "proficiency": "Intermediate", "category": "Resume"})

    # Check completeness
    missing_fields = []
    if not educations:
        missing_fields.append("Education history")
    if not skills_list:
        missing_fields.append("Key skills")
    if not experiences and not projects:
        missing_fields.append("Projects or Experience")

    is_sufficient = len(skills_list) > 0 or len(educations) > 0

    return {
        "user_id": user_id,
        "profile": profile_data,
        "skills": skills_list,
        "skill_names": [s["name"] for s in skills_list],
        "educations": educations,
        "experiences": experiences,
        "projects": projects,
        "resume": resume_info,
        "missing_critical_info": missing_fields,
        "is_sufficient": is_sufficient
    }
