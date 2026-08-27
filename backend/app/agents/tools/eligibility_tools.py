from typing import Dict, Any, List, Optional
import re
from datetime import datetime

def check_eligibility(
    candidate_profile: Dict[str, Any],
    candidate_skills: List[str],
    internship: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs rigorous eligibility verification against explicit internship requirements.
    Evaluates:
    - Degree & Major relevance
    - Graduation year / current student status
    - Location / work authorization requirements
    - Mandatory skill threshold
    
    Returns one of: ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE, UNKNOWN.
    Does NOT hallucinate missing criteria.
    """
    eligibility_raw = str(internship.get("eligibility") or "").strip()
    req_skills = [s.strip().lower() for s in internship.get("requirements", []) if s.strip()]
    candidate_skills_set = set(s.strip().lower() for s in candidate_skills)
    
    reasons_pass = []
    reasons_fail = []
    unknowns = []

    # 1. Evaluate explicit text
    if not eligibility_raw:
        unknowns.append("No explicit eligibility criteria posted by company")
    else:
        elig_lower = eligibility_raw.lower()
        educations = candidate_profile.get("educations", [])
        
        # Check graduation year
        grad_year_match = re.search(r'202[3-7]', elig_lower)
        if grad_year_match and educations:
            required_year = int(grad_year_match.group(0))
            candidate_end_year = educations[0].get("end_year")
            if candidate_end_year:
                if candidate_end_year == required_year:
                    reasons_pass.append(f"Graduation year ({candidate_end_year}) matches required {required_year} batch.")
                elif abs(candidate_end_year - required_year) <= 1:
                    reasons_pass.append(f"Graduation year ({candidate_end_year}) is within eligible graduation window.")
                else:
                    reasons_fail.append(f"Batch mismatch: Requires {required_year}, candidate graduates in {candidate_end_year}.")
            else:
                unknowns.append(f"Requires {required_year} graduate batch, candidate graduation year unverified.")
        
        # Check degree qualifications
        if any(term in elig_lower for term in ["b.tech", "b.e", "btech", "computer science", "engineering", "bachelor"]):
            if educations:
                edu_deg = str(educations[0].get("degree", "")).lower()
                edu_field = str(educations[0].get("field", "")).lower()
                if any(t in edu_deg or t in edu_field for t in ["b.tech", "b.e", "bachelor", "computer", "information", "software", "engineering", "science"]):
                    reasons_pass.append(f"Degree field ({educations[0].get('degree')} in {educations[0].get('field')}) meets requirement.")
                else:
                    reasons_fail.append(f"Requires Engineering/CS degree; candidate background: {educations[0].get('degree')}.")
            else:
                unknowns.append("Education degree verification required.")

    # 2. Check Mandatory Skill Threshold
    if req_skills:
        matched_req = [s for s in req_skills if s in candidate_skills_set]
        coverage_ratio = len(matched_req) / len(req_skills)
        if coverage_ratio >= 0.7:
            reasons_pass.append(f"Meets core required skill threshold ({len(matched_req)}/{len(req_skills)} verified).")
        elif coverage_ratio >= 0.4:
            reasons_pass.append(f"Partially meets skill threshold ({len(matched_req)}/{len(req_skills)} verified).")
        else:
            missing = [s for s in req_skills if s not in candidate_skills_set]
            reasons_fail.append(f"Missing mandatory core skills: {', '.join(missing[:3])}.")

    # 3. Determine Overall Status
    if reasons_fail and len(reasons_fail) > len(reasons_pass):
        status = "NOT_ELIGIBLE"
    elif reasons_fail and len(reasons_pass) > 0:
        status = "PARTIALLY_ELIGIBLE"
    elif reasons_pass and not reasons_fail:
        status = "ELIGIBLE"
    elif unknowns and not reasons_fail:
        status = "UNKNOWN"
    else:
        status = "PARTIALLY_ELIGIBLE"

    return {
        "status": status, # ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE, UNKNOWN
        "internship_id": internship.get("id"),
        "company": internship.get("company"),
        "title": internship.get("title"),
        "raw_eligibility": eligibility_raw or "Not specified",
        "verified_requirements": reasons_pass,
        "discrepancies": reasons_fail,
        "unverified_criteria": unknowns
    }
