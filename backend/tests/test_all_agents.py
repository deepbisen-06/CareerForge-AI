import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.vector_store import rag_store, BM25Okapi
from app.agents.matching_agent import matching_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.agents.customization_agent import FactValidator, customization_agent
from app.services.ingestion.normalizer import normalize_skill, normalize_domain
from app.services.ingestion.deduplicator import deduplicator, InternshipDeduplicator

def test_skill_normalizer():
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("golang") == "Go"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("GenAI") == "LLMs"
    assert normalize_skill("Generative AI") == "LLMs"

def test_domain_normalizer():
    assert normalize_domain("Machine Learning") == "AI/ML"
    assert normalize_domain("Web Development") == "Fullstack Development"
    assert normalize_domain("DevOps") == "Cloud & DevOps"
    assert normalize_domain("InfoSec") == "Cybersecurity"

def test_bm25_search():
    corpus = [
        "Python FastAPI backend microservices development with Docker and Redis",
        "React TypeScript frontend user interface design with Tailwind CSS",
        "Deep learning PyTorch computer vision and NLP models training",
        "Cybersecurity penetration testing network security and cryptography"
    ]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores("FastAPI Python backend")
    assert scores[0] > scores[1]
    assert scores[0] > scores[2]

def test_hybrid_rag_search():
    rag_store.ensure_indexed()
    results = rag_store.search("FastAPI Python PostgreSQL", top_k=5, candidate_skills=["Python", "FastAPI"])
    assert len(results) > 0
    assert results[0]["score"] > 0.0
    doc = results[0]["internship"]
    assert "company" in doc
    assert "title" in doc

def test_matching_agent():
    student_profile = {
        "preferred_domains": ["AI/ML"],
        "preferred_locations": ["Bangalore, India"],
        "preferred_work_mode": "Remote",
        "experiences": [{"role": "Intern", "company": "AI Lab", "description": "Built PyTorch models"}],
        "projects": [{"title": "RAG Agent", "description": "LangChain PyTorch", "technologies": ["Python", "PyTorch"]}],
        "educations": [{"degree": "B.Tech in Computer Science", "field": "Computer Science"}]
    }
    student_skills = ["Python", "PyTorch", "Machine Learning", "FastAPI"]
    internship = {
        "id": 1,
        "company": "Google",
        "title": "Machine Learning Intern",
        "domain": "AI/ML",
        "requirements": ["Python", "PyTorch", "Machine Learning"],
        "preferred_skills": ["Docker", "FastAPI"],
        "location": "Bangalore, India",
        "work_mode": "Remote"
    }
    match = matching_agent.compute_match(student_profile, student_skills, internship)
    assert match["overall_score"] >= 80.0
    assert "skills_score" in match["score_breakdown"]
    assert len(match["matched_skills"]) >= 3
    assert len(match["strengths"]) > 0

def test_skill_gap_agent():
    student_skills = [
        {"name": "Python", "proficiency": "Advanced"},
        {"name": "React", "proficiency": "Intermediate"}
    ]
    internship = {
        "id": 1,
        "company": "Amazon",
        "title": "Cloud Engineer Intern",
        "requirements": ["Python", "Docker", "Kubernetes"],
        "preferred_skills": ["AWS", "Terraform"]
    }
    report = skill_gap_agent.analyze_gaps(student_skills, internship)
    assert report["total_gaps"] >= 2
    assert report["high_priority_gaps"] >= 2
    assert len(report["action_plan"]) >= 2
    assert any(g["skill"] == "Docker" for g in report["gaps"])

def test_fact_validator():
    student_profile = {
        "full_name": "Aarav Sharma",
        "email": "student@careerbridge.ai",
        "skills": [{"name": "Python"}, {"name": "React"}],
        "experiences": [{"company": "TechCorp", "role": "Intern"}],
        "projects": [{"title": "Agent System", "technologies": ["Python"]}],
        "educations": [{"degree": "B.Tech", "institution": "NIT"}]
    }
    whitelist = FactValidator.extract_candidate_entity_whitelist(student_profile)
    assert "python" in whitelist["skills"]
    assert "techcorp" in whitelist["companies"]

    valid_text = "Experienced with Python and built Agent System at TechCorp."
    is_valid, warnings = FactValidator.validate_content(valid_text, whitelist)
    assert is_valid is True

    fake_text = "I have 10+ years of experience leading teams."
    is_valid_fake, warnings_fake = FactValidator.validate_content(fake_text, whitelist)
    assert is_valid_fake is False
    assert len(warnings_fake) > 0

def test_cover_letter_tones():
    student_profile = {
        "full_name": "Aarav Sharma",
        "email": "student@careerbridge.ai",
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "projects": [{"title": "RAG System"}],
        "experiences": [],
        "educations": []
    }
    internship = {
        "company": "Microsoft",
        "title": "Software Engineer Intern",
        "requirements": ["Python", "FastAPI"]
    }
    doc_prof = customization_agent.generate_cover_letter(student_profile, internship, tone="Professional")
    assert "Dear Hiring Team at Microsoft" in doc_prof["content"]
    assert doc_prof["metadata"]["tone"] == "Professional"

    doc_conf = customization_agent.generate_cover_letter(student_profile, internship, tone="Confident")
    assert "strong conviction" in doc_conf["content"]
    assert doc_conf["metadata"]["tone"] == "Confident"
