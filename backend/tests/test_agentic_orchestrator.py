import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.models.entities import User, Profile, Skill, UserSkill, Education, Experience, Project, Internship, SavedJob, AgentRun, AgentEvent
from app.agents.tools.profile_tools import analyze_candidate_profile
from app.agents.tools.opportunity_tools import discover_opportunities, retrieve_saved_opportunities
from app.agents.tools.matching_tools import calculate_match
from app.agents.tools.eligibility_tools import check_eligibility
from app.agents.tools.skill_gap_tools import analyze_skill_gap
from app.agents.tools.application_tools import prepare_application_package
from app.agents.tools.tracker_tools import track_application
from app.agents.orchestrator import orchestrator

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Seed User
    user = User(id=1, email="test.student@example.com", password_hash="fakehash", role="student")
    session.add(user)
    
    # Profile
    profile = Profile(
        user_id=1,
        full_name="Alex Rivera",
        career_objective="Aspiring Machine Learning Engineer",
        preferred_domains=["AI/ML", "Data Science"],
        preferred_locations=["Remote", "Bangalore"],
        preferred_work_mode="Remote"
    )
    session.add(profile)

    # Skills
    skills_data = [("Python", "AI/ML"), ("PyTorch", "AI/ML"), ("FastAPI", "Web"), ("SQL", "Data")]
    for sname, scat in skills_data:
        sk = Skill(name=sname, category=scat)
        session.add(sk)
        session.commit()
        usk = UserSkill(user_id=1, skill_id=sk.id, proficiency="Advanced")
        session.add(usk)

    # Education
    edu = Education(
        user_id=1,
        degree="B.Tech Computer Science",
        institution="Apex Institute of Technology",
        field="Artificial Intelligence",
        start_year=2021,
        end_year=2025,
        cgpa_or_percentage="8.8"
    )
    session.add(edu)

    # Project
    proj = Project(
        user_id=1,
        title="Autonomous RAG Assistant",
        description="Built end-to-end vector search retrieval with LLM ranking",
        technologies=["Python", "PyTorch", "FastAPI"]
    )
    session.add(proj)

    # Seed Internships
    opp1 = Internship(
        id=101,
        company="NeuroTech AI Labs",
        title="Machine Learning Engineering Intern",
        domain="AI/ML",
        description="Develop deep learning models and scalable PyTorch training pipelines.",
        requirements=["Python", "PyTorch", "Deep Learning"],
        preferred_skills=["Docker", "FastAPI"],
        location="Remote",
        work_mode="Remote",
        stipend="₹45,000/month",
        duration="6 months",
        eligibility="B.Tech Computer Science 2025 graduates",
        deadline="2026-09-30",
        is_active=True
    )
    opp2 = Internship(
        id=102,
        company="CloudScale Systems",
        title="Full Stack Cloud Intern",
        domain="Software Development",
        description="Build microservices and React web portals.",
        requirements=["FastAPI", "React", "PostgreSQL"],
        preferred_skills=["Docker", "AWS"],
        location="Bangalore",
        work_mode="Hybrid",
        stipend="₹30,000/month",
        duration="3 months",
        eligibility="Engineering students",
        deadline="2026-10-15",
        is_active=True
    )
    session.add(opp1)
    session.add(opp2)
    session.commit()

    yield session
    session.close()


def test_profile_tool(db_session):
    ctx = analyze_candidate_profile(user_id=1, db=db_session)
    assert ctx["is_sufficient"] is True
    assert "Python" in ctx["skill_names"]
    assert "PyTorch" in ctx["skill_names"]
    assert len(ctx["educations"]) >= 1
    assert ctx["profile"]["full_name"] == "Alex Rivera"


def test_deterministic_matching_tool(db_session):
    ctx = analyze_candidate_profile(user_id=1, db=db_session)
    opp = db_session.query(Internship).filter(Internship.id == 101).first()
    opp_dict = {
        "id": opp.id,
        "company": opp.company,
        "title": opp.title,
        "domain": opp.domain,
        "requirements": opp.requirements,
        "preferred_skills": opp.preferred_skills,
        "location": opp.location,
        "work_mode": opp.work_mode,
        "eligibility": opp.eligibility
    }

    match_res = calculate_match(
        candidate_profile=ctx,
        candidate_skills=ctx["skill_names"],
        internship=opp_dict
    )
    assert match_res["match_score"] >= 65.0
    assert "Python" in match_res["matched_skills"]
    assert len(match_res["strengths"]) > 0


def test_eligibility_tool(db_session):
    ctx = analyze_candidate_profile(user_id=1, db=db_session)
    opp = db_session.query(Internship).filter(Internship.id == 101).first()
    opp_dict = {
        "id": opp.id,
        "company": opp.company,
        "title": opp.title,
        "requirements": opp.requirements,
        "eligibility": opp.eligibility
    }

    elig = check_eligibility(
        candidate_profile=ctx,
        candidate_skills=ctx["skill_names"],
        internship=opp_dict
    )
    assert elig["status"] in ["ELIGIBLE", "PARTIALLY_ELIGIBLE"]
    assert len(elig["verified_requirements"]) > 0


def test_skill_gap_tool(db_session):
    ctx = analyze_candidate_profile(user_id=1, db=db_session)
    opp = db_session.query(Internship).filter(Internship.id == 101).first()
    opp_dict = {
        "id": opp.id,
        "company": opp.company,
        "title": opp.title,
        "requirements": opp.requirements,
        "preferred_skills": opp.preferred_skills
    }

    gaps = analyze_skill_gap(candidate_skills=ctx["skills"], internship=opp_dict)
    assert "readiness_score" in gaps
    assert len(gaps["matched_skills"]) > 0


def test_goal_1_autonomous_discovery_and_approval_gate(db_session):
    """
    Goal 1: High-level discovery & apply.
    Verifies autonomous multi-step plan, event persistence, and AWAITING_APPROVAL pause.
    """
    run = AgentRun(
        user_id=1,
        goal="Find AI/ML internships matching my profile, prioritize remote, and prepare me to apply.",
        status="PENDING",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(run)
    db_session.commit()

    completed_run = orchestrator.execute_run(run_id=run.id, db=db_session)
    
    # Verify multi-step plan was generated and executed
    assert len(completed_run.execution_plan) >= 5
    assert completed_run.status == "AWAITING_APPROVAL"
    assert "top_opportunities" in completed_run.final_summary
    assert completed_run.final_summary["application_package"] is not None

    # Verify events were persisted to DB
    events = db_session.query(AgentEvent).filter(AgentEvent.run_id == run.id).all()
    assert len(events) >= 5
    event_types = [e.event_type for e in events]
    assert "agent_run_started" in event_types
    assert "plan_created" in event_types
    assert "approval_requested" in event_types

    # Human-in-the-loop approval
    approved_run = orchestrator.approve_run(run_id=run.id, user_id=1, db=db_session, notes="Approved!")
    assert approved_run.status == "COMPLETED"
    assert approved_run.completed_at is not None


def test_goal_2_saved_jobs_prioritization(db_session):
    """
    Goal 2: Prioritize saved jobs.
    Verifies distinct plan sequence using retrieve_saved_opportunities.
    """
    # Bookmark internship 101
    sj = SavedJob(user_id=1, internship_id=101, saved_at=datetime.now(timezone.utc))
    db_session.add(sj)
    db_session.commit()

    run = AgentRun(
        user_id=1,
        goal="Analyze the internships I already saved and tell me which ones I should apply to first.",
        status="PENDING",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(run)
    db_session.commit()

    res_run = orchestrator.execute_run(run_id=run.id, db=db_session)
    tools_used = [step["tool"] for step in res_run.execution_plan]
    assert "retrieve_saved_opportunities" in tools_used
    assert "calculate_match" in tools_used
    assert res_run.status in ["COMPLETED", "AWAITING_APPROVAL"]


def test_goal_3_skill_gap_analysis(db_session):
    """
    Goal 3: Skill gap analysis roadmap.
    Verifies distinct plan focusing on skill gaps.
    """
    run = AgentRun(
        user_id=1,
        goal="Identify critical skill gaps and create a preparation roadmap for AI/ML roles.",
        status="PENDING",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(run)
    db_session.commit()

    res_run = orchestrator.execute_run(run_id=run.id, db=db_session)
    tools_used = [step["tool"] for step in res_run.execution_plan]
    assert "analyze_skill_gap" in tools_used
    assert len(res_run.execution_plan) > 0
