from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timezone
from app.database.session import get_db
from app.models.entities import User, Application, Internship
from app.schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut, InternshipOut
from app.auth.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["Application Tracker"])

def evaluate_deadline_status(deadline_str: str) -> str:
    if not deadline_str:
        return "Normal"
    try:
        d_date = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        diff = (d_date - today).days
        if diff < 0:
            return "Overdue"
        elif diff <= 2:
            return "Urgent"
        elif diff <= 7:
            return "Approaching"
        return "Normal"
    except Exception:
        return "Normal"

@router.get("/", response_model=List[ApplicationOut])
def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.updated_at.desc()).all()
    results = []
    for a in apps:
        dl_status = evaluate_deadline_status(a.deadline)
        results.append(ApplicationOut(
            id=a.id,
            user_id=a.user_id,
            internship_id=a.internship_id,
            status=a.status,
            applied_at=a.applied_at,
            deadline=a.deadline,
            notes=a.notes,
            match_score=a.match_score,
            internship=InternshipOut.model_validate(a.internship),
            created_at=a.created_at,
            updated_at=a.updated_at,
            deadline_status=dl_status
        ))
    return results

@router.post("/", response_model=ApplicationOut)
def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == app_in.internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.internship_id == app_in.internship_id
    ).first()

    if existing:
        existing.status = app_in.status
        if app_in.deadline:
            existing.deadline = app_in.deadline
        if app_in.notes:
            existing.notes = app_in.notes
        db.commit()
        db.refresh(existing)
        return ApplicationOut(
            id=existing.id,
            user_id=existing.user_id,
            internship_id=existing.internship_id,
            status=existing.status,
            applied_at=existing.applied_at,
            deadline=existing.deadline,
            notes=existing.notes,
            match_score=existing.match_score,
            internship=InternshipOut.model_validate(existing.internship),
            created_at=existing.created_at,
            updated_at=existing.updated_at,
            deadline_status=evaluate_deadline_status(existing.deadline)
        )

    app_obj = Application(
        user_id=current_user.id,
        internship_id=internship.id,
        status=app_in.status,
        deadline=app_in.deadline or internship.deadline,
        notes=app_in.notes,
        match_score=85.0
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)

    return ApplicationOut(
        id=app_obj.id,
        user_id=app_obj.user_id,
        internship_id=app_obj.internship_id,
        status=app_obj.status,
        applied_at=app_obj.applied_at,
        deadline=app_obj.deadline,
        notes=app_obj.notes,
        match_score=app_obj.match_score,
        internship=InternshipOut.model_validate(app_obj.internship),
        created_at=app_obj.created_at,
        updated_at=app_obj.updated_at,
        deadline_status=evaluate_deadline_status(app_obj.deadline)
    )

@router.put("/{id}", response_model=ApplicationOut)
def update_application(
    id: int,
    app_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == id, Application.user_id == current_user.id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_update.status:
        app_obj.status = app_update.status
        if app_update.status.upper() == "APPLIED" and not app_obj.applied_at:
            app_obj.applied_at = datetime.now(timezone.utc)
    if app_update.deadline:
        app_obj.deadline = app_update.deadline
    if app_update.notes is not None:
        app_obj.notes = app_update.notes

    db.commit()
    db.refresh(app_obj)

    return ApplicationOut(
        id=app_obj.id,
        user_id=app_obj.user_id,
        internship_id=app_obj.internship_id,
        status=app_obj.status,
        applied_at=app_obj.applied_at,
        deadline=app_obj.deadline,
        notes=app_obj.notes,
        match_score=app_obj.match_score,
        internship=InternshipOut.model_validate(app_obj.internship),
        created_at=app_obj.created_at,
        updated_at=app_obj.updated_at,
        deadline_status=evaluate_deadline_status(app_obj.deadline)
    )

@router.delete("/{id}")
def delete_application(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == id, Application.user_id == current_user.id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_obj)
    db.commit()
    return {"message": "Application removed from tracker"}

@router.get("/stats")
def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.user_id == current_user.id).all()
    stats = {
        "SAVED": 0, "PLANNED": 0, "APPLIED": 0, "ASSESSMENT": 0,
        "INTERVIEW": 0, "OFFER": 0, "SELECTED": 0, "REJECTED": 0, "WITHDRAWN": 0
    }
    for a in apps:
        s = a.status.upper()
        if s in stats:
            stats[s] += 1
        else:
            stats[s] = 1
    return {
        "total": len(apps),
        "status_counts": stats
    }
