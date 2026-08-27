from typing import Dict, Any, List
from app.agents.skill_gap_agent import skill_gap_agent

def analyze_skill_gap(
    candidate_skills: List[Dict[str, Any]],
    internship: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes deterministic skill gap matrix computation.
    Produces prioritized list of critical missing, partial, and matched skills
    with estimated hours and learning resources.
    """
    report = skill_gap_agent.analyze_gaps(
        student_skills=candidate_skills,
        internship=internship
    )

    user_skill_names = set(s.get("name", "").lower() for s in candidate_skills if isinstance(s, dict))
    all_job_skills = internship.get("requirements", []) + internship.get("preferred_skills", [])
    matched_skills = [s for s in all_job_skills if s.lower() in user_skill_names]

    gaps = report.get("gaps", [])
    total_hours = sum(g.get("estimated_hours", 0) for g in gaps)
    critical = [g for g in gaps if g.get("priority") == "HIGH"]
    desirable = [g for g in gaps if g.get("priority") in ["MEDIUM", "LOW"]]

    return {
        "internship_id": internship.get("id"),
        "company": internship.get("company"),
        "role": internship.get("title"),
        "readiness_score": report.get("overall_readiness", report.get("readiness_score", 0.0)),
        "total_estimated_hours": total_hours,
        "summary": f"{len(matched_skills)} skills matched, {len(critical)} critical gap(s) identified.",
        "critical_missing_skills": critical,
        "desirable_missing_skills": desirable,
        "matched_skills": matched_skills,
        "all_gaps": gaps,
        "action_plan": report.get("action_plan", [])
    }
