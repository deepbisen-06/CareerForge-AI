from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.session import get_db
from app.auth.deps import get_current_admin_user
from app.models.entities import User, Internship, Application, InterviewSession, Skill, InternshipSkill
from app.schemas.schemas import AdminStatsOut, InternshipOut, InternshipCreate, InternshipUpdate, IngestionRequestIn
from app.services.ingestion.pipeline import ingestion_pipeline
from app.rag.vector_store import rag_store

router = APIRouter(prefix="/admin", tags=["Admin Management"])

@router.get("/stats", response_model=AdminStatsOut)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Returns platform-wide metrics for administrators.
    """
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_internships = db.query(Internship).count()
    active_internships = db.query(Internship).filter(Internship.is_active == True).count()
    total_applications = db.query(Application).count()
    total_interviews = db.query(InterviewSession).count()
    rag_indexed = len(rag_store.documents)

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_internships": total_internships,
        "active_internships": active_internships,
        "total_applications": total_applications,
        "total_interviews_taken": total_interviews,
        "rag_indexed_count": rag_indexed,
        "ai_status": "online"
    }

@router.get("/internships", response_model=List[InternshipOut])
def list_admin_internships(
    skip: int = 0,
    limit: int = 50,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    query = db.query(Internship)
    if domain and domain.lower() != "all":
        query = query.filter(Internship.domain == domain)
    return query.order_by(Internship.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/internships", response_model=InternshipOut)
def create_admin_internship(
    payload: InternshipCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    raw_dict = payload.model_dump()
    result = ingestion_pipeline.process_raw_dataset(db, [raw_dict], refresh_rag=True)
    created = db.query(Internship).order_by(Internship.created_at.desc()).first()
    return created

@router.put("/internships/{internship_id}", response_model=InternshipOut)
def update_admin_internship(
    internship_id: int,
    payload: InternshipUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    job = db.query(Internship).filter(Internship.id == internship_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
    
    db.commit()
    db.refresh(job)
    rag_store.ensure_indexed()
    return job

@router.delete("/internships/{internship_id}")
def delete_admin_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    job = db.query(Internship).filter(Internship.id == internship_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    db.delete(job)
    db.commit()
    
    # Reindex active in RAG
    all_active = db.query(Internship).filter(Internship.is_active == True).all()
    records = [{
        "id": it.id, "company": it.company, "title": it.title, "domain": it.domain,
        "description": it.description, "requirements": it.requirements or [],
        "preferred_skills": it.preferred_skills or [], "location": it.location,
        "work_mode": it.work_mode, "stipend": it.stipend, "duration": it.duration,
        "eligibility": it.eligibility, "deadline": it.deadline,
        "application_url": it.application_url, "source": it.source,
        "source_type": it.source_type, "is_active": it.is_active, "is_demo": it.is_demo
    } for it in all_active]
    rag_store.index_internships(records)
    
    return {"status": "success", "message": f"Internship #{internship_id} deleted"}

@router.post("/ingest")
def trigger_ingestion(
    payload: IngestionRequestIn,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Triggers automated ingestion pipeline over curated feed or dataset.
    """
    import os
    import json
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "internships", "internships_200.json")
    if not os.path.exists(data_file):
        from seed_generator import generate_internships
        raw_data = generate_internships(payload.limit or 220)
    else:
        with open(data_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

    result = ingestion_pipeline.process_raw_dataset(db, raw_data, refresh_rag=payload.refresh_vectors)
    return result

@router.post("/rag/reindex")
def trigger_rag_reindex(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Forces a complete rebuild of the Hybrid Dense + BM25 RAG index.
    """
    all_active = db.query(Internship).filter(Internship.is_active == True).all()
    records = [{
        "id": it.id, "company": it.company, "title": it.title, "domain": it.domain,
        "description": it.description, "requirements": it.requirements or [],
        "preferred_skills": it.preferred_skills or [], "location": it.location,
        "work_mode": it.work_mode, "stipend": it.stipend, "duration": it.duration,
        "eligibility": it.eligibility, "deadline": it.deadline,
        "application_url": it.application_url, "source": it.source,
        "source_type": it.source_type, "is_active": it.is_active, "is_demo": it.is_demo
    } for it in all_active]
    count = rag_store.index_internships(records)
    return {"status": "success", "indexed_documents": count}
