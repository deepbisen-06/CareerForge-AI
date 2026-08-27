"""
Deduplicator Service for Internship Ingestion.
Uses composite keys (source + source_job_id, normalized company + title + location) to prevent duplicate insertion.
"""
from typing import Dict, Any, List, Tuple, Set
from sqlalchemy.orm import Session
from app.models.entities import Internship

class InternshipDeduplicator:
    @staticmethod
    def generate_dedup_key(company: str, title: str, location: str) -> str:
        c = re_clean(company)
        t = re_clean(title)
        l = re_clean(location)
        return f"{c}::{t}::{l}"

    def filter_duplicates(self, db: Session, incoming_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """
        Filters out duplicate records against both the database and the incoming batch.
        Returns: (unique_records, duplicates_count)
        """
        # 1. Fetch existing keys from DB
        existing_jobs = db.query(Internship.company, Internship.title, Internship.location, Internship.source_job_id).all()
        existing_keys: Set[str] = set()
        existing_source_ids: Set[str] = set()

        for comp, titl, loc, src_id in existing_jobs:
            existing_keys.add(self.generate_dedup_key(comp, titl, loc))
            if src_id:
                existing_source_ids.add(str(src_id))

        unique_records = []
        batch_seen_keys: Set[str] = set()
        duplicates_count = 0

        for item in incoming_records:
            comp = item.get("company", "")
            titl = item.get("title", "")
            loc = item.get("location", "")
            src_id = item.get("source_job_id")

            key = self.generate_dedup_key(comp, titl, loc)

            if src_id and str(src_id) in existing_source_ids:
                duplicates_count += 1
                continue

            if key in existing_keys or key in batch_seen_keys:
                duplicates_count += 1
                continue

            batch_seen_keys.add(key)
            if src_id:
                existing_source_ids.add(str(src_id))
            unique_records.append(item)

        return unique_records, duplicates_count

def re_clean(text: str) -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', str(text or '')).lower()

deduplicator = InternshipDeduplicator()
