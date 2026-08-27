from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.database.session import get_db
from app.models.entities import Internship, User, SavedJob
from app.schemas.schemas import InternshipOut, SavedJobOut, ProvenanceInfo
from app.auth.deps import get_current_user
from app.rag.vector_store import rag_store
from app.agents.matching_agent import matching_agent

router = APIRouter(prefix="/internships", tags=["Internships & RAG"])

@router.get("/", response_model=List[InternshipOut])
def get_internships(
    q: Optional[str] = Query(None, description="Semantic search query"),
    domain: Optional[str] = Query(None, description="Domain filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    work_mode: Optional[str] = Query(None, description="Work mode filter"),
    source_type: Optional[str] = Query(None, description="Source type filter (CURATED, LIVE, DEMO)"),
    is_active_only: bool = Query(True, description="Filter only active opportunities"),
    limit: int = Query(50, ge=1, le=250),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_skills = [us.skill.name for us in current_user.user_skills] if current_user else []
    user_saved_ids = set()
    pref_dict = None
    if current_user:
        user_saved = db.query(SavedJob.internship_id).filter(SavedJob.user_id == current_user.id).all()
        user_saved_ids = set(s[0] for s in user_saved)
        if current_user.profile:
            pref_dict = {
                "preferred_domains": current_user.profile.preferred_domains or [],
                "preferred_locations": current_user.profile.preferred_locations or [],
                "preferred_work_mode": current_user.profile.preferred_work_mode or "Any",
            }
    
    # 1. Hybrid RAG Search Flow
    if q:
        results = rag_store.search(
            query=q,
            top_k=limit,
            domain_filter=domain,
            location_filter=location,
            work_mode_filter=work_mode,
            source_type_filter=source_type,
            is_active_only=is_active_only,
            candidate_skills=user_skills,
            candidate_preferences=pref_dict
        )
        internship_list = []
        for r in results:
            doc = r["internship"]
            match_val = round(r["score"] * 100.0, 1)
            
            if current_user:
                prof_dict = {
                    "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
                    "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
                    "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
                    "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
                    "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
                    "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
                }
                match_res = matching_agent.compute_match(prof_dict, user_skills, doc)
                match_val = match_res["overall_score"]

            c_at = doc.get("created_at")
            if not isinstance(c_at, datetime):
                c_at = datetime.now(timezone.utc)

            prov_raw = doc.get("provenance")
            prov_obj = None
            if prov_raw:
                prov_obj = ProvenanceInfo(
                    retrieval_score=prov_raw.get("retrieval_score", 0.0),
                    rerank_score=prov_raw.get("rerank_score", 0.0),
                    positive_reasons=prov_raw.get("positive_reasons", []),
                    negative_reasons=prov_raw.get("negative_reasons", []),
                    source_type=prov_raw.get("source_type", "CURATED"),
                    retrieved_at=prov_raw.get("retrieved_at")
                )

            internship_list.append(InternshipOut(
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
                source_url=doc.get("source_url"),
                company_logo_url=doc.get("company_logo_url"),
                is_active=doc.get("is_active", True),
                is_demo=doc.get("is_demo", True),
                is_saved=(doc["id"] in user_saved_ids),
                created_at=c_at,
                posted_at=doc.get("posted_at"),
                last_verified_at=doc.get("last_verified_at"),
                match_score=match_val,
                provenance=prov_obj
            ))
        return internship_list

    # 2. Database Filter Flow
    query_obj = db.query(Internship)
    if is_active_only:
        query_obj = query_obj.filter(Internship.is_active == True)
    if domain and domain.lower() not in ["all", "any", ""]:
        query_obj = query_obj.filter(Internship.domain.ilike(f"%{domain}%"))
    if location and location.lower() not in ["all", "any", ""]:
        query_obj = query_obj.filter(Internship.location.ilike(f"%{location}%"))
    if work_mode and work_mode.lower() not in ["all", "any", ""]:
        query_obj = query_obj.filter(Internship.work_mode.ilike(f"%{work_mode}%"))
    if source_type and source_type.lower() not in ["all", "any", ""]:
        query_obj = query_obj.filter(Internship.source_type == source_type.upper())

    internships = query_obj.order_by(Internship.id.desc()).limit(limit).all()
    
    output = []
    for item in internships:
        item_dict = {
            "id": item.id, "company": item.company, "title": item.title, "domain": item.domain,
            "requirements": item.requirements or [], "preferred_skills": item.preferred_skills or [],
            "location": item.location, "work_mode": item.work_mode, "eligibility": item.eligibility
        }
        match_val = None
        if current_user:
            prof_dict = {
                "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
                "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
                "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
                "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
                "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
                "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
            }
            res = matching_agent.compute_match(prof_dict, user_skills, item_dict)
            match_val = res["overall_score"]

        output.append(InternshipOut(
            id=item.id,
            company=item.company,
            title=item.title,
            domain=item.domain,
            description=item.description,
            requirements=item.requirements or [],
            preferred_skills=item.preferred_skills or [],
            location=item.location,
            work_mode=item.work_mode,
            stipend=item.stipend,
            duration=item.duration,
            eligibility=item.eligibility,
            deadline=item.deadline,
            application_url=item.application_url,
            source=item.source,
            source_type=item.source_type,
            source_url=item.source_url,
            company_logo_url=item.company_logo_url,
            is_active=item.is_active,
            is_demo=item.is_demo,
            is_saved=(item.id in user_saved_ids),
            created_at=item.created_at,
            posted_at=item.posted_at,
            last_verified_at=item.last_verified_at,
            match_score=match_val
        ))

    if current_user:
        output.sort(key=lambda x: x.match_score or 0, reverse=True)

    return output

@router.get("/saved", response_model=List[SavedJobOut])
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all internships bookmarked by the authenticated user.
    """
    saved_records = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).order_by(SavedJob.saved_at.desc()).all()
    user_skills = [us.skill.name for us in current_user.user_skills]
    
    output = []
    for s in saved_records:
        job = s.internship
        prof_dict = {
            "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
            "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
            "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
            "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
            "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
            "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
        }
        res = matching_agent.compute_match(prof_dict, user_skills, {
            "id": job.id, "company": job.company, "title": job.title, "domain": job.domain,
            "requirements": job.requirements or [], "preferred_skills": job.preferred_skills or [],
            "location": job.location, "work_mode": job.work_mode, "eligibility": job.eligibility
        })
        
        job_out = InternshipOut(
            id=job.id, company=job.company, title=job.title, domain=job.domain,
            description=job.description, requirements=job.requirements or [],
            preferred_skills=job.preferred_skills or [], location=job.location,
            work_mode=job.work_mode, stipend=job.stipend, duration=job.duration,
            eligibility=job.eligibility, deadline=job.deadline,
            application_url=job.application_url, source=job.source,
            source_type=job.source_type, company_logo_url=job.company_logo_url,
            is_active=job.is_active, is_demo=job.is_demo, is_saved=True,
            created_at=job.created_at, posted_at=job.posted_at,
            last_verified_at=job.last_verified_at, match_score=res["overall_score"]
        )
        output.append(SavedJobOut(
            id=s.id, user_id=s.user_id, internship_id=s.internship_id,
            saved_at=s.saved_at, internship=job_out
        ))
    return output

@router.post("/{id}/save")
def toggle_save_internship(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Saves/bookmarks an internship. Idempotent.
    """
    job = db.query(Internship).filter(Internship.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Internship not found")
        
    existing = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.internship_id == id).first()
    if existing:
        return {"status": "already_saved", "saved": True, "message": "Internship already bookmarked"}
        
    saved = SavedJob(user_id=current_user.id, internship_id=id)
    db.add(saved)
    db.commit()
    return {"status": "saved", "saved": True, "message": f"Saved {job.title} at {job.company}"}

@router.delete("/{id}/save")
def unsave_internship(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Removes a bookmarked internship.
    """
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.internship_id == id).first()
    if saved:
        db.delete(saved)
        db.commit()
    return {"status": "unsaved", "saved": False, "message": "Bookmark removed"}

@router.get("/{id}", response_model=InternshipOut)
def get_internship_detail(
    id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(Internship).filter(Internship.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")

    match_val = None
    is_saved = False
    if current_user:
        is_saved = bool(db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.internship_id == id).first())
        user_skills = [us.skill.name for us in current_user.user_skills]
        prof_dict = {
            "preferred_domains": current_user.profile.preferred_domains if current_user.profile else [],
            "preferred_locations": current_user.profile.preferred_locations if current_user.profile else [],
            "preferred_work_mode": current_user.profile.preferred_work_mode if current_user.profile else "Any",
            "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in current_user.experiences],
            "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in current_user.projects],
            "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in current_user.educations]
        }
        item_dict = {
            "id": item.id, "company": item.company, "title": item.title, "domain": item.domain,
            "requirements": item.requirements or [], "preferred_skills": item.preferred_skills or [],
            "location": item.location, "work_mode": item.work_mode, "eligibility": item.eligibility
        }
        res = matching_agent.compute_match(prof_dict, user_skills, item_dict)
        match_val = res["overall_score"]

    return InternshipOut(
        id=item.id,
        company=item.company,
        title=item.title,
        domain=item.domain,
        description=item.description,
        requirements=item.requirements or [],
        preferred_skills=item.preferred_skills or [],
        location=item.location,
        work_mode=item.work_mode,
        stipend=item.stipend,
        duration=item.duration,
        eligibility=item.eligibility,
        deadline=item.deadline,
        application_url=item.application_url,
        source=item.source,
        source_type=item.source_type,
        source_url=item.source_url,
        company_logo_url=item.company_logo_url,
        is_active=item.is_active,
        is_demo=item.is_demo,
        is_saved=is_saved,
        created_at=item.created_at,
        posted_at=item.posted_at,
        last_verified_at=item.last_verified_at,
        match_score=match_val
    )
