import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.agents.matching_agent import matching_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.agents.resume_agent import resume_agent
from app.agents.customization_agent import customization_agent
from app.agents.interview_agent import interview_agent
from app.rag.vector_store import rag_store

client = TestClient(app)

# 1. Test Root & Health
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CareerBridge AI"
    assert data["status"] == "online"

# 2. Test Auth & User Creation
def test_auth_flow():
    login_payload = {
        "email": "demo@careerbridge.ai",
        "password": "Demo@123"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "demo@careerbridge.ai"

# 3. Test Profile Endpoints
def test_profile_endpoints():
    login_payload = {"email": "demo@careerbridge.ai", "password": "Demo@123"}
    token = client.post("/api/v1/auth/login", json=login_payload).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/profile/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Aarav Sharma"
    assert data["completion_percentage"] >= 80

# 4. Test RAG Vector Search & Internship Explorer
def test_rag_and_internships():
    login_payload = {"email": "demo@careerbridge.ai", "password": "Demo@123"}
    token = client.post("/api/v1/auth/login", json=login_payload).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure RAG store is initialized
    rag_store.ensure_indexed()

    # List all
    res = client.get("/api/v1/internships/?limit=10", headers=headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    assert "match_score" in items[0]

    # Semantic search with query
    search_res = client.get("/api/v1/internships/?q=machine+learning+pytorch&limit=5", headers=headers)
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) > 0

# 5. Test Deterministic Matching Agent
def test_matching_agent():
    profile = {
        "preferred_domains": ["AI/ML"],
        "preferred_locations": ["Bangalore, India"],
        "preferred_work_mode": "Remote",
        "experiences": [{"role": "ML Intern", "company": "Tech", "description": "PyTorch models"}],
        "projects": [{"title": "Vision", "description": "OpenCV and PyTorch", "technologies": ["Python", "PyTorch"]}],
        "educations": [{"degree": "B.Tech", "field": "Computer Science"}]
    }
    skills = ["Python", "PyTorch", "Machine Learning"]
    internship = {
        "id": 1,
        "company": "Google",
        "title": "Machine Learning Intern",
        "domain": "AI/ML",
        "requirements": ["Python", "PyTorch", "Machine Learning"],
        "preferred_skills": ["Docker"],
        "location": "Bangalore, India",
        "work_mode": "Remote",
        "eligibility": "B.Tech students"
    }

    match_result = matching_agent.compute_match(profile, skills, internship)
    assert match_result["overall_score"] >= 80.0
    assert "skills_score" in match_result["score_breakdown"]
    assert len(match_result["matched_skills"]) >= 3
    assert len(match_result["strengths"]) > 0

# 6. Test Skill Gap Analysis
def test_skill_gap_agent():
    user_skills = [{"name": "Python", "proficiency": "Advanced"}]
    internship = {
        "id": 1,
        "company": "Scale AI",
        "title": "AI Engineer Intern",
        "requirements": ["Python", "PyTorch", "Docker"],
        "preferred_skills": ["Kubernetes"]
    }
    gap_rep = skill_gap_agent.analyze_gaps(user_skills, internship)
    assert gap_rep["total_gaps"] >= 2
    assert gap_rep["high_priority_gaps"] >= 1
    assert len(gap_rep["action_plan"]) > 0

# 7. Test Resume Customization & Cover Letter
def test_customization_agent():
    profile = {
        "full_name": "Aarav Sharma",
        "email": "demo@careerbridge.ai",
        "phone": "+91 98765 43210",
        "skills": [{"name": "Python"}, {"name": "PyTorch"}],
        "projects": [{"title": "RAG Engine", "description": "Built search engine", "technologies": ["Python", "PyTorch"]}],
        "experiences": [{"role": "Intern", "company": "Co", "description": "Engineered APIs"}],
        "educations": [{"degree": "B.Tech", "institution": "NIT"}]
    }
    internship = {
        "id": 1,
        "company": "Anthropic",
        "title": "Research Intern",
        "requirements": ["Python", "PyTorch"]
    }

    tailored_resume = customization_agent.generate_tailored_resume(profile, "Raw text", internship)
    assert "Aarav Sharma" in tailored_resume["content"]
    assert "Anthropic" in tailored_resume["content"]

    cover_letter = customization_agent.generate_cover_letter(profile, internship)
    assert "Anthropic" in cover_letter["content"]
    assert "Research Intern" in cover_letter["content"]

# 8. Test Interview Agent
def test_interview_agent():
    internship = {"company": "Microsoft", "title": "Software Engineer Intern", "requirements": ["Python", "FastAPI"]}
    profile = {"full_name": "Aarav", "projects": [{"title": "Microservices"}]}

    questions = interview_agent.generate_question_bank(internship, profile, count=4)
    assert len(questions) == 4
    assert questions[0]["category"] in ["Technical", "Behavioral", "HR", "Resume-based", "Role-specific"]

    prep_plan = interview_agent.generate_5_day_plan(internship, profile)
    assert len(prep_plan) == 5

    eval_res = interview_agent.evaluate_answer(
        question="How do you handle API latency?",
        ideal_answer="Use Redis caching, indexing, and asynchronous coroutines.",
        user_answer="I use Redis caching to store frequently accessed records and index foreign keys to reduce query latency significantly."
    )
    assert eval_res["score"] >= 7.0
    assert "accuracy" in eval_res["criteria"]

# 9. Test Application Kanban Tracker
def test_applications_flow():
    login_payload = {"email": "demo@careerbridge.ai", "password": "Demo@123"}
    token = client.post("/api/v1/auth/login", json=login_payload).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/applications/", json={"internship_id": 2, "status": "SAVED"}, headers=headers)
    assert create_res.status_code == 200
    app_id = create_res.json()["id"]

    update_res = client.put(f"/api/v1/applications/{app_id}", json={"status": "INTERVIEW", "notes": "Round 1 passed"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "INTERVIEW"

    stats_res = client.get("/api/v1/applications/stats", headers=headers)
    assert stats_res.status_code == 200
    assert stats_res.json()["status_counts"]["INTERVIEW"] >= 1
