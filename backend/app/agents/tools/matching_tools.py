from typing import Dict, Any, List
from app.agents.matching_agent import matching_agent

def calculate_match(
    candidate_profile: Dict[str, Any],
    candidate_skills: List[str],
    internship: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes the deterministic, explainable multi-factor compatibility scoring engine.
    Calculates weighted score (skills, experience, projects, education, preferences),
    factor breakdown, strengths, weaknesses, and eligibility flags.
    """
    match_result = matching_agent.compute_match(
        student_profile=candidate_profile,
        student_skills=candidate_skills,
        internship=internship
    )

    return {
        "internship_id": internship.get("id"),
        "company": internship.get("company"),
        "title": internship.get("title"),
        "domain": internship.get("domain"),
        "location": internship.get("location"),
        "work_mode": internship.get("work_mode"),
        "match_score": match_result.get("overall_score", match_result.get("match_score", 0.0)),
        "is_eligible": match_result.get("is_eligible", True),
        "factor_breakdown": match_result.get("score_breakdown", match_result.get("factor_breakdown", {})),
        "strengths": match_result.get("strengths", []),
        "weaknesses": match_result.get("discrepancies", match_result.get("weaknesses", [])),
        "recommendation": match_result.get("recommendation", ""),
        "missing_skills": match_result.get("missing_skills", []),
        "matched_skills": match_result.get("matched_skills", [])
    }
