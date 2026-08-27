import json
import os
import re
import math
from datetime import datetime, timezone
import numpy as np
from typing import List, Dict, Any, Optional, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger("careerbridge.rag")

class BM25Okapi:
    """
    Lightweight, fast in-memory BM25 indexer for lexical keyword scoring.
    """
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / self.corpus_size if self.corpus_size > 0 else 0.0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []
        
        nd: Dict[str, int] = {}
        for doc in corpus:
            self.doc_len.append(len(doc))
            frequencies: Dict[str, int] = {}
            for word in doc:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                nd[word] = nd.get(word, 0) + 1

        for word, freq in nd.items():
            # Standard Lucene/Okapi smoothed IDF
            self.idf[word] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query: List[str]) -> np.ndarray:
        scores = np.zeros(self.corpus_size)
        if self.corpus_size == 0:
            return scores
        
        for q in query:
            if q not in self.idf:
                continue
            idf_val = self.idf[q]
            for idx, doc_freq in enumerate(self.doc_freqs):
                freq = doc_freq.get(q, 0)
                if freq == 0:
                    continue
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / (self.avgdl or 1.0)))
                scores[idx] += idf_val * (numerator / denominator)
                
        # Normalize 0-1
        max_s = np.max(scores)
        if max_s > 0:
            scores = scores / max_s
        return scores


class RAGVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.bm25_index: Optional[BM25Okapi] = None
        self.is_indexed: bool = False

    def tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r'\b[a-zA-Z0-9_+#\.-]+\b', text.lower()) if len(w) > 1]

    def build_document_text(self, record: Dict[str, Any]) -> str:
        req_str = " ".join(record.get("requirements", []))
        pref_str = " ".join(record.get("preferred_skills", []))
        return (
            f"Title: {record.get('title', '')} "
            f"Company: {record.get('company', '')} "
            f"Domain: {record.get('domain', '')} "
            f"Location: {record.get('location', '')} "
            f"Work Mode: {record.get('work_mode', '')} "
            f"Required Skills: {req_str} "
            f"Preferred Skills: {pref_str} "
            f"Eligibility: {record.get('eligibility', '')} "
            f"Description: {record.get('description', '')}"
        )

    def index_internships(self, internships: List[Dict[str, Any]]) -> int:
        if not internships:
            return 0
        
        self.documents = internships
        corpus_text = [self.build_document_text(item) for item in internships]
        corpus_tokens = [self.tokenize(text) for text in corpus_text]
        
        # 1. Build Dense Semantic TF-IDF Matrix
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=10000
        )
        self.embeddings_matrix = self.vectorizer.fit_transform(corpus_text)
        
        # 2. Build Sparse BM25 Index
        self.bm25_index = BM25Okapi(corpus_tokens)
        
        self.is_indexed = True
        logger.info(f"Hybrid RAG Engine successfully indexed {len(internships)} internships (Dense + BM25).")
        return len(internships)

    def ensure_indexed(self):
        if not self.is_indexed:
            try:
                from app.database.session import SessionLocal
                from app.models.entities import Internship
                db = SessionLocal()
                items = db.query(Internship).all()
                if items:
                    records = [{
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
                        "is_active": getattr(item, "is_active", True),
                        "is_demo": item.is_demo
                    } for item in items]
                    self.index_internships(records)
                db.close()
            except Exception as e:
                logger.error(f"Error auto-indexing RAG vector store: {e}")

    def generate_provenance(
        self,
        doc: Dict[str, Any],
        retrieval_score: float,
        rerank_score: float,
        candidate_skills: Optional[List[str]] = None,
        candidate_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates explainable positive reasons and negative discrepancies for trust & auditability.
        """
        positive_reasons = []
        negative_reasons = []
        user_skills_lower = set(s.lower() for s in (candidate_skills or []))
        
        doc_req = doc.get("requirements", [])
        doc_pref = doc.get("preferred_skills", [])
        
        matched_req = [s for s in doc_req if s.lower() in user_skills_lower]
        missing_req = [s for s in doc_req if s.lower() not in user_skills_lower]
        
        if matched_req:
            positive_reasons.append(f"✓ Strong alignment on core skills: {', '.join(matched_req[:3])}")
        if missing_req:
            negative_reasons.append(f"✗ Requires additional proficiency in: {', '.join(missing_req[:2])}")
            
        if candidate_preferences:
            pref_mode = candidate_preferences.get("preferred_work_mode", "Any")
            if pref_mode.lower() != "any" and pref_mode.lower() in doc.get("work_mode", "").lower():
                positive_reasons.append(f"✓ Matches preferred {doc.get('work_mode')} work format")
            
            pref_domains = candidate_preferences.get("preferred_domains", [])
            if any(d.lower() in doc.get("domain", "").lower() for d in pref_domains):
                positive_reasons.append(f"✓ Directly in your target {doc.get('domain')} career field")

        if not positive_reasons:
            positive_reasons.append(f"✓ Foundational {doc.get('domain', 'technology')} opportunity matching role profile")

        return {
            "retrieval_score": round(float(retrieval_score), 3),
            "rerank_score": round(float(rerank_score), 3),
            "positive_reasons": positive_reasons,
            "negative_reasons": negative_reasons,
            "source_type": doc.get("source_type", "CURATED"),
            "retrieved_at": datetime.now(timezone.utc)
        }

    def search(
        self,
        query: str,
        top_k: int = 10,
        domain_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        work_mode_filter: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        is_active_only: bool = True,
        candidate_skills: Optional[List[str]] = None,
        candidate_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        self.ensure_indexed()

        if not self.is_indexed or len(self.documents) == 0:
            return []

        # 1. Augment Query with Candidate Skills Context
        augmented_query = query or ""
        if candidate_skills:
            augmented_query += " " + " ".join(candidate_skills)

        # 2. Dense Semantic Cosine Scoring
        dense_scores = np.zeros(len(self.documents))
        if self.vectorizer and self.embeddings_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([augmented_query])
                dense_scores = cosine_similarity(query_vec, self.embeddings_matrix).flatten()
            except Exception as e:
                logger.warning(f"Dense scoring warning: {e}")

        # 3. Sparse Lexical BM25 Scoring
        sparse_scores = np.zeros(len(self.documents))
        if self.bm25_index:
            query_tokens = self.tokenize(augmented_query)
            if query_tokens:
                sparse_scores = self.bm25_index.get_scores(query_tokens)

        # 4. Hybrid Score Fusion (60% Dense Semantic + 40% Sparse Lexical)
        hybrid_scores = (dense_scores * 0.60) + (sparse_scores * 0.40)

        # 5. Metadata Hard Filtering & Cross-Encoder Skill Reranking
        candidate_results = []
        user_skills_set = set(s.lower() for s in (candidate_skills or []))

        for idx, doc in enumerate(self.documents):
            # Active filter
            if is_active_only and not doc.get("is_active", True):
                continue

            # Domain Filter
            if domain_filter and domain_filter.lower() not in ["all", "any", ""]:
                if doc.get("domain", "").lower() != domain_filter.lower():
                    continue

            # Location Filter
            if location_filter and location_filter.lower() not in ["all", "any", ""]:
                if location_filter.lower() not in doc.get("location", "").lower():
                    continue

            # Work Mode Filter
            if work_mode_filter and work_mode_filter.lower() not in ["all", "any", ""]:
                if doc.get("work_mode", "").lower() != work_mode_filter.lower():
                    continue

            # Source Type Filter
            if source_type_filter and source_type_filter.lower() not in ["all", "any", ""]:
                if doc.get("source_type", "").lower() != source_type_filter.lower():
                    continue

            base_retrieval = float(hybrid_scores[idx]) if idx < len(hybrid_scores) else 0.0

            # Re-ranking calculation: Skill Exactness Boost + Preference Match Boost
            rerank_boost = 0.0
            doc_all_skills = [s.lower() for s in (doc.get("requirements", []) + doc.get("preferred_skills", []))]
            if doc_all_skills and user_skills_set:
                matched_cnt = sum(1 for us in user_skills_set if us in doc_all_skills)
                rerank_boost = (matched_cnt / len(doc_all_skills)) * 0.35

            final_rerank_score = min(1.0, base_retrieval + rerank_boost)

            provenance = self.generate_provenance(
                doc=doc,
                retrieval_score=base_retrieval,
                rerank_score=final_rerank_score,
                candidate_skills=candidate_skills,
                candidate_preferences=candidate_preferences
            )

            doc_with_provenance = doc.copy()
            doc_with_provenance["provenance"] = provenance

            candidate_results.append({
                "internship": doc_with_provenance,
                "score": final_rerank_score,
                "retrieval_score": base_retrieval
            })

        # Sort by reranked score descending
        candidate_results.sort(key=lambda x: x["score"], reverse=True)
        return candidate_results[:top_k]

rag_store = RAGVectorStore()
