from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import User, Internship, RecommendationFeedback
from app.schemas.schemas import MatchExplanationOut, RecommendationFeedbackIn
from app.auth.deps import get_current_user
from app.agents.matching_agent import matching_agent

router = APIRouter(prefix="/matching", tags=["Job-Resume Matching"])

@router.get("/{internship_id}", response_model=MatchExplanationOut)
def get_match_explanation(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    user_skills = [us.skill.name for us in current_user.user_skills]
    prof_dict = {
        "full_name": current_user.profile.full_name if current_user.profile else "Student",
        "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
        "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
        "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
        "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
        "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
        "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
    }
    
    internship_dict = {
        "id": internship.id,
        "company": internship.company,
        "title": internship.title,
        "domain": internship.domain,
        "requirements": internship.requirements or [],
        "preferred_skills": internship.preferred_skills or [],
        "location": internship.location,
        "work_mode": internship.work_mode,
        "eligibility": internship.eligibility
    }

    result = matching_agent.compute_match(prof_dict, user_skills, internship_dict)
    return MatchExplanationOut(**result)

@router.post("/feedback")
def submit_recommendation_feedback(
    payload: RecommendationFeedbackIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records student rating (thumbs up / thumbs down + category) on recommendations.
    """
    job = db.query(Internship).filter(Internship.id == payload.internship_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Internship not found")

    feedback = RecommendationFeedback(
        user_id=current_user.id,
        internship_id=payload.internship_id,
        is_positive=payload.is_positive,
        reason_category=payload.reason_category,
        notes=payload.notes
    )
    db.add(feedback)
    db.commit()

    return {"status": "success", "message": "Thank you for your feedback! It will help refine future recommendations."}
