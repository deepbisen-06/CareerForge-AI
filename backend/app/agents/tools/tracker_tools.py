from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Application, Internship
from datetime import datetime, timezone

def track_application(
    user_id: int,
    internship_id: int,
    status: str = "PREPARATION_READY",
    match_score: float = 0.0,
    notes: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Creates or updates an application tracking record without silently claiming submission.
    Supported statuses: DISCOVERED, SHORTLISTED, PREPARATION_READY, AWAITING_USER_APPROVAL, APPLIED.
    """
    if not db:
        return {
            "status": status,
            "internship_id": internship_id,
            "tracked": True,
            "simulated": True
        }

    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        return {"error": f"Internship {internship_id} not found", "tracked": False}

    existing = db.query(Application).filter(
        Application.user_id == user_id,
        Application.internship_id == internship_id
    ).first()

    if existing:
        existing.status = status
        if match_score > 0:
            existing.match_score = match_score
        if notes:
            existing.notes = notes
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        record_id = existing.id
    else:
        new_app = Application(
            user_id=user_id,
            internship_id=internship_id,
            status=status,
            match_score=match_score,
            notes=notes or "Shortlisted by CareerForge Autonomous Agent"
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        record_id = new_app.id

    return {
        "application_id": record_id,
        "internship_id": internship_id,
        "company": internship.company,
        "title": internship.title,
        "status": status,
        "match_score": match_score,
        "tracked": True
    }
