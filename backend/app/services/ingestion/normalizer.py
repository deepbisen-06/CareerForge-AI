"""
Canonical Data Normalizer for Internship Ingestion.
Standardizes company names, domains, work modes, stipends, and technical skills.
"""
from typing import Dict, Any, List
import re

SYNONYM_SKILL_MAP = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "genai": "LLMs",
    "generative ai": "LLMs",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "git": "Git",
    "github": "Git",
    "sql": "SQL",
    "c++": "C++",
    "cpp": "C++",
    "golang": "Go",
    "go": "Go",
    "rag": "RAG",
    "langchain": "LangChain",
    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "algorithms": "Algorithms"
}

DOMAIN_CANONICAL_MAP = {
    "ai/ml": "AI/ML",
    "artificial intelligence": "AI/ML",
    "machine learning": "AI/ML",
    "data science": "Data Science",
    "analytics": "Data Science",
    "software engineering": "Software Development",
    "software development": "Software Development",
    "web development": "Fullstack Development",
    "fullstack": "Fullstack Development",
    "full stack": "Fullstack Development",
    "frontend": "Frontend Development",
    "backend": "Software Development",
    "cloud": "Cloud & DevOps",
    "devops": "Cloud & DevOps",
    "cybersecurity": "Cybersecurity",
    "infosec": "Cybersecurity",
    "security": "Cybersecurity",
    "mobile": "Mobile Development",
    "android": "Mobile Development",
    "ios": "Mobile Development",
    "robotics": "Robotics & IoT",
    "iot": "Robotics & IoT",
    "product": "Product Management"
}

def normalize_skill(skill_str: str) -> str:
    cleaned = skill_str.strip().lower()
    return SYNONYM_SKILL_MAP.get(cleaned, skill_str.strip())

def normalize_domain(domain_str: str) -> str:
    cleaned = domain_str.strip().lower()
    return DOMAIN_CANONICAL_MAP.get(cleaned, "Software Development")

def normalize_work_mode(mode_str: str) -> str:
    cleaned = (mode_str or "").strip().lower()
    if "remote" in cleaned:
        return "Remote"
    elif "hybrid" in cleaned:
        return "Hybrid"
    elif "onsite" in cleaned or "office" in cleaned:
        return "Onsite"
    return "Remote"

def normalize_internship_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleanses and standardizes an internship record dictionary.
    """
    company = (raw.get("company") or raw.get("company_name") or "Tech Organization").strip()
    title = (raw.get("title") or raw.get("job_title") or "Software Engineering Intern").strip()
    domain = normalize_domain(raw.get("domain") or "Software Development")
    work_mode = normalize_work_mode(raw.get("work_mode") or raw.get("job_type") or "Remote")
    location = (raw.get("location") or "Bangalore, India").strip()
    
    # Skills normalization
    raw_req = raw.get("requirements") or raw.get("required_skills") or []
    if isinstance(raw_req, str):
        raw_req = [s.strip() for s in raw_req.split(",") if s.strip()]
    normalized_req = list(dict.fromkeys([normalize_skill(s) for s in raw_req if s.strip()]))
    
    raw_pref = raw.get("preferred_skills") or []
    if isinstance(raw_pref, str):
        raw_pref = [s.strip() for s in raw_pref.split(",") if s.strip()]
    normalized_pref = list(dict.fromkeys([normalize_skill(s) for s in raw_pref if s.strip()]))

    stipend = raw.get("stipend") or raw.get("salary_stipend") or "₹25,000 - ₹35,000 / month"
    duration = raw.get("duration") or "3-6 Months"
    eligibility = raw.get("eligibility") or raw.get("experience_required") or "B.Tech / B.E / M.Tech in CS/IT or related branch"
    deadline = raw.get("deadline") or raw.get("last_date") or "Rolling Applications"
    app_url = raw.get("application_url") or "https://careers.example.com"
    source = raw.get("source") or raw.get("source_platform") or "Curated Dataset"
    source_type = raw.get("source_type") or "CURATED"
    company_logo_url = raw.get("company_logo_url") or None

    return {
        "company": company,
        "title": title,
        "domain": domain,
        "description": (raw.get("description") or raw.get("job_description") or f"{title} opportunity at {company}.").strip(),
        "requirements": normalized_req or ["Python", "Problem Solving"],
        "preferred_skills": normalized_pref,
        "location": location,
        "work_mode": work_mode,
        "stipend": stipend,
        "duration": duration,
        "eligibility": eligibility,
        "deadline": deadline,
        "application_url": app_url,
        "source": source,
        "source_type": source_type,
        "source_job_id": raw.get("source_job_id") or None,
        "company_logo_url": company_logo_url,
        "is_active": True,
        "is_demo": raw.get("is_demo", False)
    }
