from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.rag.vector_store import rag_store
from app.models.entities import Internship, SavedJob

def discover_opportunities(
    query: Optional[str] = None,
    domain: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    candidate_skills: Optional[List[str]] = None,
    candidate_preferences: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Discovers relevant internships via Hybrid RAG (BM25 + TF-IDF Vector Search)
    and database verification. Filters by domain, location, and work mode.
    Never fabricates opportunities.
    """
    rag_store.ensure_indexed()

    clean_domain = None if not domain or domain.lower() in ["all", "any", "none"] else domain
    clean_location = None if not location or location.lower() in ["all", "any", "none"] else location
    clean_work_mode = None if not work_mode or work_mode.lower() in ["all", "any", "none"] else work_mode

    search_query = query or ""
    if not search_query and clean_domain:
        search_query = clean_domain

    raw_results = rag_store.search(
        query=search_query,
        top_k=limit,
        domain_filter=clean_domain,
        location_filter=clean_location,
        work_mode_filter=clean_work_mode,
        candidate_skills=candidate_skills,
        candidate_preferences=candidate_preferences
    )

    # Unwrap from {"internship": {...}, "score": ...} if needed
    results = []
    for item in raw_results:
        if isinstance(item, dict) and "internship" in item:
            opp_dict = item["internship"].copy()
            opp_dict["retrieval_score"] = item.get("retrieval_score", 0.0)
            opp_dict["rerank_score"] = item.get("score", 0.0)
            results.append(opp_dict)
        elif isinstance(item, dict):
            results.append(item)

    # Fallback to direct DB query if RAG returned empty
    if not results and db:
        q = db.query(Internship).filter(Internship.is_active == True)
        if clean_domain:
            q = q.filter(Internship.domain.ilike(f"%{clean_domain}%"))
        if clean_work_mode:
            q = q.filter(Internship.work_mode.ilike(f"%{clean_work_mode}%"))
        if clean_location:
            q = q.filter(Internship.location.ilike(f"%{clean_location}%"))
        items = q.limit(limit).all()
        results = [{
            "id": item.id,
            "company": item.company,
            "title": item.title,
            "domain": item.domain,
            "description": item.description,
            "requirements": item.requirements or [],
            "preferred_skills": item.preferred_skills or [],
            "location": item.location,
            "work_mode": item.work_mode,
            "stipend": item.stipend,
            "duration": item.duration,
            "eligibility": item.eligibility,
            "deadline": item.deadline,
            "application_url": item.application_url,
            "source": item.source,
            "source_type": getattr(item, "source_type", "CURATED"),
            "company_logo_url": getattr(item, "company_logo_url", None),
            "is_active": item.is_active,
            "is_demo": item.is_demo
        } for item in items]

    return {
        "count": len(results),
        "opportunities": results,
        "filters_applied": {
            "query": query,
            "domain": clean_domain,
            "location": clean_location,
            "work_mode": clean_work_mode
        }
    }


def retrieve_saved_opportunities(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Retrieves opportunities already saved or bookmarked by the candidate.
    """
    saved_entries = db.query(SavedJob).filter(SavedJob.user_id == user_id).all()
    opportunities = []
    for s in saved_entries:
        if s.internship:
            opportunities.append({
                "id": s.internship.id,
                "company": s.internship.company,
                "title": s.internship.title,
                "domain": s.internship.domain,
                "description": s.internship.description,
                "requirements": s.internship.requirements or [],
                "preferred_skills": s.internship.preferred_skills or [],
                "location": s.internship.location,
                "work_mode": s.internship.work_mode,
                "stipend": s.internship.stipend,
                "duration": s.internship.duration,
                "eligibility": s.internship.eligibility,
                "deadline": s.internship.deadline,
                "application_url": s.internship.application_url,
                "source": s.internship.source,
                "source_type": getattr(s.internship, "source_type", "CURATED"),
                "saved_at": s.saved_at.isoformat() if s.saved_at else None
            })
    return {
        "count": len(opportunities),
        "opportunities": opportunities
    }
