from typing import Dict, Any, List
from app.services.ingestion.normalizer import normalize_skill

LEARNING_RESOURCES_DB = {
    "Docker": [
        {"title": "Docker for Developers — Official Quickstart", "url": "https://docs.docker.com/get-started/", "type": "Documentation"},
        {"title": "Containerization & Multi-stage Builds Practical Guide", "url": "https://docker-curriculum.com/", "type": "Interactive Tutorial"}
    ],
    "Kubernetes": [
        {"title": "Kubernetes Basics & Pod Orchestration", "url": "https://kubernetes.io/docs/tutorials/", "type": "Official Lab"},
        {"title": "K8s Architecture in 60 Minutes", "url": "https://cloud.google.com/learn/what-is-kubernetes", "type": "Guide"}
    ],
    "AWS": [
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/", "type": "Free Course"},
        {"title": "Deploying Microservices on AWS ECS & Lambda", "url": "https://aws.amazon.com/getting-started/hands-on/", "type": "Lab"}
    ],
    "PyTorch": [
        {"title": "Deep Learning with PyTorch: A 60 Minute Blitz", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html", "type": "Official Tutorial"},
        {"title": "Neural Networks & Backpropagation from Scratch", "url": "https://karpathy.ai/zero-to-hero.html", "type": "Video Series"}
    ],
    "FastAPI": [
        {"title": "FastAPI Official Interactive Tutorial & Async APIs", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "Documentation"},
        {"title": "Building Production Backend with SQLAlchemy & Pydantic", "url": "https://fastapi.tiangolo.com/advanced/", "type": "Project Guide"}
    ],
    "React": [
        {"title": "React 19 Official Documentation & Hooks Guide", "url": "https://react.dev/learn", "type": "Documentation"},
        {"title": "Fullstack React & Modern State Management", "url": "https://fullstackopen.com/en/", "type": "Course"}
    ],
    "PostgreSQL": [
        {"title": "PostgreSQL Performance Optimization & Indexing", "url": "https://www.postgresql.org/docs/current/tutorial.html", "type": "Documentation"},
        {"title": "SQL Practice & Query Execution Plans", "url": "https://sqlbolt.com/", "type": "Interactive Tutorial"}
    ],
    "RAG": [
        {"title": "Retrieval Augmented Generation with LangChain & Vector DBs", "url": "https://python.langchain.com/docs/tutorials/rag/", "type": "Tutorial"},
        {"title": "Embedding Models & Re-ranking Best Practices", "url": "https://huggingface.co/blog/rag", "type": "Guide"}
    ],
    "Redis": [
        {"title": "Redis University — Fast In-Memory Data Structures", "url": "https://university.redis.com/", "type": "Interactive Lab"},
        {"title": "Caching Architecture Patterns with Redis", "url": "https://redis.io/docs/latest/develop/use/", "type": "Guide"}
    ]
}

class SkillGapAgent:
    def analyze_gaps(
        self,
        student_skills: List[Dict[str, Any]], # [{"name": "Python", "proficiency": "Advanced"}]
        internship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyzes required and preferred skills for the internship against student skills.
        Identifies MATCHED, PARTIAL, and MISSING skills, assigns priorities,
        and generates actionable learning recommendations.
        """
        user_skills_map = {normalize_skill(s["name"]).lower(): s.get("proficiency", "Intermediate") for s in student_skills}
        req_skills = [normalize_skill(s) for s in internship.get("requirements", [])]
        pref_skills = [normalize_skill(s) for s in internship.get("preferred_skills", [])]

        gaps: List[Dict[str, Any]] = []
        matched_count = 0
        total_eval_skills = len(req_skills) + len(pref_skills)

        # 1. Evaluate Core Requirements
        for skill_name in req_skills:
            s_lower = skill_name.lower()
            if s_lower in user_skills_map:
                prof = user_skills_map[s_lower]
                if prof in ["Advanced", "Expert"]:
                    matched_count += 1
                else: # Beginner or Intermediate
                    matched_count += 0.7
                    gaps.append({
                        "skill": skill_name,
                        "current_level": prof,
                        "required_level": "Advanced",
                        "gap_score": 0.3,
                        "priority": "MEDIUM",
                        "status_tag": "PARTIAL",
                        "recommendation": f"Strengthen {skill_name} from {prof} to Advanced by building a production-level feature and optimizing latency.",
                        "estimated_hours": 8,
                        "learning_resources": LEARNING_RESOURCES_DB.get(skill_name, [
                            {"title": f"Mastering {skill_name} Guide", "url": "https://devdocs.io", "type": "Docs"}
                        ])
                    })
            else:
                gaps.append({
                    "skill": skill_name,
                    "current_level": "None",
                    "required_level": "Intermediate",
                    "gap_score": 1.0,
                    "priority": "HIGH",
                    "status_tag": "MISSING",
                    "recommendation": f"Core requirement: Acquire hands-on fundamentals of {skill_name}. Complete a guided practical project before technical screening.",
                    "estimated_hours": 15,
                    "learning_resources": LEARNING_RESOURCES_DB.get(skill_name, [
                        {"title": f"{skill_name} Core Fundamentals & Hands-on Lab", "url": "https://freecodecamp.org", "type": "Tutorial"}
                    ])
                })

        # 2. Evaluate Preferred Skills
        for skill_name in pref_skills:
            s_lower = skill_name.lower()
            if s_lower in user_skills_map:
                matched_count += 1
            else:
                gaps.append({
                    "skill": skill_name,
                    "current_level": "None",
                    "required_level": "Beginner/Intermediate",
                    "gap_score": 0.6,
                    "priority": "LOW",
                    "status_tag": "MISSING",
                    "recommendation": f"Preferred bonus skill: Familiarize yourself with {skill_name} architectural concepts to stand out in interviews.",
                    "estimated_hours": 6,
                    "learning_resources": LEARNING_RESOURCES_DB.get(skill_name, [
                        {"title": f"{skill_name} Overview & Quickstart", "url": "https://roadmap.sh", "type": "Overview"}
                    ])
                })

        # Priority Sorting: HIGH -> MEDIUM -> LOW
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        gaps.sort(key=lambda x: priority_order.get(x["priority"], 3))

        high_count = sum(1 for g in gaps if g["priority"] == "HIGH")
        overall_readiness = round(max(20.0, min(100.0, (matched_count / (total_eval_skills or 1)) * 100.0)), 1)

        # Synthesize Action Plan
        action_plan = []
        if high_count > 0:
            high_skills = [g["skill"] for g in gaps if g["priority"] == "HIGH"]
            action_plan.append(f"Phase 1 (Days 1-4): Focus urgently on {', '.join(high_skills[:3])} through practical labs.")
        med_skills = [g["skill"] for g in gaps if g["priority"] == "MEDIUM"]
        if med_skills:
            action_plan.append(f"Phase 2 (Days 5-7): Level up {', '.join(med_skills[:2])} by showcasing best practices in your project code.")
        action_plan.append("Phase 3: Update your tailored resume to highlight completed project milestones.")

        return {
            "internship_id": internship.get("id"),
            "company": internship.get("company"),
            "title": internship.get("title"),
            "overall_readiness": overall_readiness,
            "total_gaps": len(gaps),
            "high_priority_gaps": high_count,
            "gaps": gaps,
            "action_plan": action_plan
        }

skill_gap_agent = SkillGapAgent()
