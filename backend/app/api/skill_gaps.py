from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import User, Internship, SkillGap
from app.schemas.schemas import SkillGapReportOut, SkillGapItem
from app.auth.deps import get_current_user
from app.agents.skill_gap_agent import skill_gap_agent

router = APIRouter(prefix="/skill-gaps", tags=["Skill Gap Analysis"])

@router.get("/{internship_id}", response_model=SkillGapReportOut)
def get_skill_gaps_for_internship(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    user_skills = [{"name": us.skill.name, "proficiency": us.proficiency} for us in current_user.user_skills]
    
    internship_dict = {
        "id": internship.id,
        "company": internship.company,
        "title": internship.title,
        "requirements": internship.requirements or [],
        "preferred_skills": internship.preferred_skills or []
    }

    report = skill_gap_agent.analyze_gaps(user_skills, internship_dict)

    # Persist or update SkillGap records in database
    for gap in report["gaps"]:
        existing = db.query(SkillGap).filter(
            SkillGap.user_id == current_user.id,
            SkillGap.internship_id == internship.id,
            SkillGap.skill == gap["skill"]
        ).first()

        if not existing:
            db.add(SkillGap(
                user_id=current_user.id,
                internship_id=internship.id,
                skill=gap["skill"],
                current_level=gap["current_level"],
                required_level=gap["required_level"],
                gap_score=gap["gap_score"],
                priority=gap["priority"],
                recommendation=gap["recommendation"],
                estimated_hours=gap["estimated_hours"],
                learning_resources=gap["learning_resources"]
            ))
        else:
            existing.current_level = gap["current_level"]
            existing.required_level = gap["required_level"]
            existing.priority = gap["priority"]
            existing.recommendation = gap["recommendation"]
    
    db.commit()
    return SkillGapReportOut(**report)
