"""
Modular Ingestion Pipeline for CareerBridge AI.
Orchestrates: Fetch -> Parse -> Normalize -> Deduplicate -> Validate -> Persist -> Vector Index.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from app.models.entities import Internship, Skill, InternshipSkill
from app.services.ingestion.normalizer import normalize_internship_record
from app.services.ingestion.deduplicator import deduplicator
from app.rag.vector_store import rag_store

logger = logging.getLogger("careerbridge.ingestion")

class IngestionPipeline:
    def process_raw_dataset(
        self,
        db: Session,
        raw_items: List[Dict[str, Any]],
        refresh_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Processes and inserts raw records through the ingestion pipeline.
        """
        # 1. Normalize
        normalized_records = [normalize_internship_record(item) for item in raw_items]
        
        # 2. Validate
        valid_records = []
        invalid_count = 0
        for item in normalized_records:
            if not item.get("company") or not item.get("title") or not item.get("description"):
                invalid_count += 1
                continue
            valid_records.append(item)

        # 3. Deduplicate
        unique_records, duplicate_count = deduplicator.filter_duplicates(db, valid_records)

        # 4. Fetch / Cache canonical skills
        all_skills = db.query(Skill).all()
        skill_map = {s.name.lower(): s.id for s in all_skills}

        # 5. Persist to DB
        inserted_count = 0
        indexed_items = []

        for r in unique_records:
            new_job = Internship(
                company=r["company"],
                title=r["title"],
                domain=r["domain"],
                description=r["description"],
                requirements=r["requirements"],
                preferred_skills=r["preferred_skills"],
                location=r["location"],
                work_mode=r["work_mode"],
                stipend=r["stipend"],
                duration=r["duration"],
                eligibility=r["eligibility"],
                deadline=r["deadline"],
                application_url=r["application_url"],
                source=r["source"],
                source_type=r["source_type"],
                source_job_id=r.get("source_job_id"),
                company_logo_url=r.get("company_logo_url"),
                is_active=True,
                is_demo=r.get("is_demo", False),
                posted_at=datetime.now(timezone.utc),
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(new_job)
            db.flush()

            # Attach Skill Relationships
            for s_name in r["requirements"]:
                s_id = skill_map.get(s_name.lower())
                if s_id:
                    db.add(InternshipSkill(internship_id=new_job.id, skill_id=s_id, required=True, importance=1.0))
            for s_name in r["preferred_skills"]:
                s_id = skill_map.get(s_name.lower())
                if s_id:
                    db.add(InternshipSkill(internship_id=new_job.id, skill_id=s_id, required=False, importance=0.6))

            r_dict = r.copy()
            r_dict["id"] = new_job.id
            indexed_items.append(r_dict)
            inserted_count += 1

        db.commit()

        # 6. Incrementally Index into RAG Vector Store
        if refresh_rag and indexed_items:
            # Reindex all active DB items to maintain vector consistency
            all_active = db.query(Internship).filter(Internship.is_active == True).all()
            all_records = [{
                "id": it.id,
                "company": it.company,
                "title": it.title,
                "domain": it.domain,
                "description": it.description,
                "requirements": it.requirements or [],
                "preferred_skills": it.preferred_skills or [],
                "location": it.location,
                "work_mode": it.work_mode,
                "stipend": it.stipend,
                "duration": it.duration,
                "eligibility": it.eligibility,
                "deadline": it.deadline,
                "application_url": it.application_url,
                "source": it.source,
                "source_type": it.source_type,
                "company_logo_url": it.company_logo_url,
                "is_active": it.is_active,
                "is_demo": it.is_demo
            } for it in all_active]
            rag_store.index_internships(all_records)
            logger.info(f"RAG store reindexed with {len(all_records)} opportunities.")

        return {
            "status": "completed",
            "total_received": len(raw_items),
            "valid_records": len(valid_records),
            "duplicates_skipped": duplicate_count,
            "invalid_skipped": invalid_count,
            "inserted_count": inserted_count,
            "rag_reindexed": refresh_rag
        }

ingestion_pipeline = IngestionPipeline()
