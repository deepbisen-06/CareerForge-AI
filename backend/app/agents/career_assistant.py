from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entities import User, Profile, Resume, Internship, Application, SkillGap
from app.agents.matching_agent import matching_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.rag.vector_store import rag_store
from app.core.llm_provider import get_llm_provider

class CareerAssistantAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    # --- Tool Definitions ---
    def tool_get_user_profile(self, db: Session, user_id: int) -> Dict[str, Any]:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return {"status": "error", "message": "Profile not found"}
        
        user_skills = [us.skill.name for us in profile.user.user_skills]
        return {
            "name": profile.full_name,
            "domains": profile.preferred_domains,
            "skills": user_skills,
            "preferred_mode": profile.preferred_work_mode,
            "preferred_stipend": profile.preferred_stipend
        }

    def tool_get_resume_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
        if not resume:
            return {"status": "error", "message": "No resume uploaded yet"}
        return {
            "file_name": resume.file_name,
            "score": resume.resume_score,
            "strengths": resume.strengths,
            "weaknesses": resume.weaknesses,
            "recommendations": resume.recommendations
        }

    def tool_search_internships(self, db: Session, query: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        results = rag_store.search(query=query, top_k=5, domain_filter=domain)
        output = []
        for r in results:
            doc = r["internship"]
            output.append({
                "id": doc.get("id"),
                "company": doc.get("company"),
                "title": doc.get("title"),
                "domain": doc.get("domain"),
                "stipend": doc.get("stipend"),
                "work_mode": doc.get("work_mode"),
                "location": doc.get("location"),
                "deadline": doc.get("deadline")
            })
        return output

    def tool_get_match_score(self, db: Session, user_id: int, internship_id: int) -> Dict[str, Any]:
        user = db.query(User).filter(User.id == user_id).first()
        internship = db.query(Internship).filter(Internship.id == internship_id).first()
        if not user or not internship:
            return {"status": "error", "message": "User or internship not found"}

        user_skills = [us.skill.name for us in user.user_skills]
        profile_dict = {
            "full_name": user.profile.full_name if user.profile else "Student",
            "preferred_domains": user.profile.preferred_domains if user.profile else [],
            "preferred_locations": user.profile.preferred_locations if user.profile else [],
            "preferred_work_mode": user.profile.preferred_work_mode if user.profile else "Any",
            "experiences": [{"company": e.company, "role": e.role, "description": e.description} for e in user.experiences],
            "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in user.projects],
            "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field} for ed in user.educations]
        }
        internship_dict = {
            "id": internship.id,
            "company": internship.company,
            "title": internship.title,
            "domain": internship.domain,
            "requirements": internship.requirements,
            "preferred_skills": internship.preferred_skills,
            "location": internship.location,
            "work_mode": internship.work_mode,
            "eligibility": internship.eligibility
        }
        return matching_agent.compute_match(profile_dict, user_skills, internship_dict)

    def tool_get_applications(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        apps = db.query(Application).filter(Application.user_id == user_id).all()
        return [
            {
                "id": a.id,
                "company": a.internship.company,
                "title": a.internship.title,
                "status": a.status,
                "deadline": a.deadline,
                "match_score": a.match_score
            }
            for a in apps
        ]

    def tool_get_upcoming_deadlines(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        apps = db.query(Application).filter(Application.user_id == user_id).all()
        upcoming = [a for a in apps if a.deadline]
        upcoming.sort(key=lambda x: x.deadline)
        return [
            {
                "company": a.internship.company,
                "title": a.internship.title,
                "status": a.status,
                "deadline": a.deadline
            }
            for a in upcoming[:5]
        ]

    def process_message(
        self,
        db: Session,
        user_id: int,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Interprets student intent, dispatches internal tools, and synthesizes a context-aware response.
        """
        msg_lower = user_message.lower()
        tool_calls_executed = []
        context_data = {}

        # 1. Dispatch Tools Based on Intent
        if any(term in msg_lower for term in ["recommend", "which internship", "best job", "apply to", "internship suggestions"]):
            tool_calls_executed.append({"tool": "search_internships", "args": {"query": "AI ML Software Engineer"}})
            # Load user skills
            user = db.query(User).filter(User.id == user_id).first()
            u_skills = [us.skill.name for us in user.user_skills] if user else []
            search_results = rag_store.search(query=user_message, top_k=3, candidate_skills=u_skills)
            context_data["internships"] = [r["internship"] for r in search_results]

        elif any(term in msg_lower for term in ["deadline", "due date", "pending application", "my application", "status"]):
            tool_calls_executed.append({"tool": "get_upcoming_deadlines", "args": {"user_id": user_id}})
            context_data["deadlines"] = self.tool_get_upcoming_deadlines(db, user_id)
            context_data["applications"] = self.tool_get_applications(db, user_id)

        elif any(term in msg_lower for term in ["resume", "ats score", "improve my resume", "resume health"]):
            tool_calls_executed.append({"tool": "get_resume_summary", "args": {"user_id": user_id}})
            context_data["resume"] = self.tool_get_resume_summary(db, user_id)

        elif any(term in msg_lower for term in ["skill gap", "missing skill", "what should i learn", "upskill"]):
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                first_app = db.query(Application).filter(Application.user_id == user_id).first()
                target_job = first_app.internship if first_app else db.query(Internship).first()
                if target_job:
                    tool_calls_executed.append({"tool": "get_skill_gaps", "args": {"internship_id": target_job.id}})
                    u_skills = [{"name": us.skill.name, "proficiency": us.proficiency} for us in user.user_skills]
                    job_dict = {
                        "id": target_job.id, "company": target_job.company, "title": target_job.title,
                        "requirements": target_job.requirements, "preferred_skills": target_job.preferred_skills
                    }
                    context_data["skill_gaps"] = skill_gap_agent.analyze_gaps(u_skills, job_dict)

        # 2. Synthesize Grounded Natural Language Response
        response_text = ""
        if "internships" in context_data and context_data["internships"]:
            top_jobs = context_data["internships"]
            job_bullet_points = []
            for j in top_jobs:
                job_bullet_points.append(
                    f"• **{j.get('title')}** at **{j.get('company')}** ({j.get('location')}) — Stipend: {j.get('stipend')}, Mode: {j.get('work_mode')}"
                )
            response_text = (
                f"Based on your profile, technical skills, and career preferences, here are the top recommended internships for you:\n\n"
                + "\n".join(job_bullet_points) +
                "\n\nYou can click on any internship in your Explorer to view your explainable compatibility score breakdown, inspect skill gaps, and generate tailored application materials."
            )

        elif "deadlines" in context_data or "applications" in context_data:
            apps = context_data.get("applications", [])
            deadlines = context_data.get("deadlines", [])
            if apps:
                app_lines = [f"• **{a['company']}** ({a['title']}) — Status: `{a['status']}`, Deadline: {a['deadline'] or 'N/A'}" for a in apps]
                response_text = (
                    f"Here is the current status of your internship applications:\n\n"
                    + "\n".join(app_lines) +
                    f"\n\nYou have {len(deadlines)} upcoming deadline(s) recorded in your tracker. Ensure your tailored resumes and cover letters are submitted before the closing dates!"
                )
            else:
                response_text = "You currently have 0 active applications in your Kanban tracker. Browse recommended internships and click **'Add to Tracker'** to manage your submissions."

        elif "resume" in context_data:
            r = context_data["resume"]
            if r.get("status") == "error":
                response_text = "You haven't uploaded a resume yet! Navigate to the **Resume Intelligence** tab to upload your PDF/DOCX and receive an instant ATS score and section audit."
            else:
                strengths_str = "\n".join([f"• ✓ {s}" for s in r.get("strengths", [])[:3]])
                recs_str = "\n".join([f"• 💡 {rec}" for rec in r.get("recommendations", [])[:2]])
                response_text = (
                    f"Your resume **{r.get('file_name')}** has an overall ATS score of **{r.get('score')}/100**.\n\n"
                    f"**Identified Strengths:**\n{strengths_str}\n\n"
                    f"**Top Recommendations:**\n{recs_str}"
                )

        elif "skill_gaps" in context_data:
            sg = context_data["skill_gaps"]
            gaps_list = sg.get("gaps", [])
            high_gaps = [g for g in gaps_list if g["priority"] == "HIGH"]
            high_str = ", ".join([g["skill"] for g in high_gaps]) if high_gaps else "None (all primary requirements met!)"
            response_text = (
                f"For the **{sg.get('title')}** role at **{sg.get('company')}**, your overall readiness is **{sg.get('overall_readiness')}%**.\n\n"
                f"• **High-Priority Skill Gaps:** {high_str}\n"
                f"• **Action Plan:** {sg.get('action_plan', ['Review learning resources in Skill Gaps tab'])[0]}\n\n"
                f"Check the **Skill Gaps** tab to access guided tutorials and project roadmaps to close these gaps rapidly."
            )

        else:
            # Default helpful assistant guidance
            response_text = (
                f"I'm your **CareerBridge AI Assistant**! I can help you with:\n\n"
                f"1. 🎯 **Internship Recommendations**: Ask *'Which internship should I apply to?'*\n"
                f"2. 🔍 **Explainable Matching**: Ask *'Why am I a good match for Google or Microsoft?'*\n"
                f"3. 📊 **Skill Gap Roadmaps**: Ask *'What skills am I missing?'*\n"
                f"4. 📝 **Document Tailoring**: Generate ATS-optimized resumes and role-specific cover letters.\n"
                f"5. 🎙️ **Interview Preparation**: Practice with AI Mock Interviews and 5-Day study plans.\n"
                f"6. 📅 **Application Tracking**: Check *'What applications are pending?'* or approaching deadlines.\n\n"
                f"How can I assist your career journey right now?"
            )

        return {
            "response": response_text,
            "tool_calls": tool_calls_executed
        }

career_assistant_agent = CareerAssistantAgent()
