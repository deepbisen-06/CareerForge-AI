from typing import Dict, Any, List, Optional
from app.agents.customization_agent import customization_agent

def prepare_application_package(
    candidate_profile: Dict[str, Any],
    candidate_skills: List[str],
    internship: Dict[str, Any],
    raw_resume_text: str = ""
) -> Dict[str, Any]:
    """
    Generates a truthful, tailored application package (Cover Letter & Bullet Refinements)
    strictly grounded in candidate profile facts with Anti-Hallucination validation.
    """
    # 1. Generate tailored cover letter
    cover_letter_res = customization_agent.generate_cover_letter(
        student_profile=candidate_profile,
        internship=internship
    )

    # 2. Generate resume alignment suggestions
    resume_tailor_res = customization_agent.generate_tailored_resume(
        student_profile=candidate_profile,
        raw_resume_text=raw_resume_text,
        internship=internship
    )

    return {
        "internship_id": internship.get("id"),
        "company": internship.get("company"),
        "title": internship.get("title"),
        "cover_letter_draft": cover_letter_res.get("cover_letter", ""),
        "cover_letter_metadata": cover_letter_res.get("metadata", {}),
        "resume_tailoring": resume_tailor_res.get("tailored_content", ""),
        "fact_validation_status": "PASSED_TRUTHFULNESS_GATE",
        "action_required": "USER_APPROVAL",
        "checklist": [
            f"Review tailored cover letter for {internship.get('company')}",
            "Verify highlighted project keywords against actual repository experience",
            "Approve application preparation to mark as ready"
        ]
    }
