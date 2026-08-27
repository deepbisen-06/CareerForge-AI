import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.entities import AgentRun, AgentEvent
from app.core.llm_provider import get_llm_provider
from app.agents.tools.profile_tools import analyze_candidate_profile
from app.agents.tools.opportunity_tools import discover_opportunities, retrieve_saved_opportunities
from app.agents.tools.matching_tools import calculate_match
from app.agents.tools.eligibility_tools import check_eligibility
from app.agents.tools.skill_gap_tools import analyze_skill_gap
from app.agents.tools.application_tools import prepare_application_package
from app.agents.tools.tracker_tools import track_application

logger = logging.getLogger("careerforge.orchestrator")

AVAILABLE_TOOLS_SPEC = [
    {
        "name": "analyze_candidate_profile",
        "description": "Analyzes the user's skills, education, projects, experience, and uploaded resume to establish candidate context.",
        "parameters": {}
    },
    {
        "name": "discover_opportunities",
        "description": "Searches and retrieves verified internships using Hybrid RAG (BM25 + Dense Semantic Vector Search) based on role domain, location, work mode, and query.",
        "parameters": {
            "query": "Optional free-text search query (e.g. 'Machine Learning', 'Frontend')",
            "domain": "Optional domain (e.g. 'AI/ML', 'Software Development', 'Data Science', 'Cloud/DevOps')",
            "location": "Optional location (e.g. 'Bangalore', 'Hyderabad', 'Remote')",
            "work_mode": "Optional work mode ('Remote', 'Hybrid', 'Onsite', 'Any')"
        }
    },
    {
        "name": "retrieve_saved_opportunities",
        "description": "Retrieves internships already saved or bookmarked by the user.",
        "parameters": {}
    },
    {
        "name": "calculate_match",
        "description": "Computes deterministic, auditable multi-factor match score (0-100%) and factor breakdown for candidate against discovered opportunities.",
        "parameters": {}
    },
    {
        "name": "check_eligibility",
        "description": "Evaluates candidate against explicit graduation timing, degree requirements, and location constraints, returning ELIGIBLE, PARTIALLY_ELIGIBLE, or NOT_ELIGIBLE.",
        "parameters": {}
    },
    {
        "name": "analyze_skill_gap",
        "description": "Performs skill-gap analysis for top opportunities, producing prioritized missing skills, estimated study hours, and curated resources.",
        "parameters": {}
    },
    {
        "name": "prepare_application_package",
        "description": "Generates truthful, fact-validated tailored cover letter and resume adaptations for the highest match opportunity. Requires user approval before submission.",
        "parameters": {}
    },
    {
        "name": "track_application",
        "description": "Records or updates application tracking status in the database.",
        "parameters": {
            "status": "Target status ('SHORTLISTED', 'PREPARATION_READY', 'AWAITING_USER_APPROVAL')"
        }
    }
]

class AutonomousAgentOrchestrator:
    """
    CareerForge AI Core Autonomous Orchestrator.
    Grounded in Google Gemini ADK planning, multi-step execution loop,
    real-time event streaming, and human-in-the-loop approval.
    """

    def plan_with_gemini(
        self,
        goal: str,
        candidate_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Uses Google Gemini to reason over the user's high-level goal and candidate context,
        producing a dynamic, ordered tool execution plan.
        """
        system_instruction = (
            "You are CareerForge AI, an autonomous internship task planner. "
            "Your role is to analyze the student's high-level goal and available tools, "
            "then formulate an optimal, sequential execution plan. "
            "Do NOT hallucinate tools outside the provided list. "
            "Output valid JSON ONLY with a 'plan' array containing steps: {step, tool, description, params}."
        )

        prompt = f"""
Goal: "{goal}"

Candidate Profile Summary:
- Domains: {candidate_summary.get('profile', {}).get('preferred_domains', ['Software Development'])}
- Work Mode: {candidate_summary.get('profile', {}).get('preferred_work_mode', 'Any')}
- Key Skills: {candidate_summary.get('skill_names', [])[:8]}

Available Tools:
{json.dumps(AVAILABLE_TOOLS_SPEC, indent=2)}

Create an execution plan tailored specifically to accomplish this goal.
Rules:
1. If the goal involves finding/applying to internships: start with analyze_candidate_profile -> discover_opportunities -> calculate_match -> check_eligibility -> analyze_skill_gap -> prepare_application_package -> track_application.
2. If the goal is about already saved jobs: start with retrieve_saved_opportunities -> calculate_match -> check_eligibility.
3. If the goal is focused on skill gaps: start with analyze_candidate_profile -> discover_opportunities -> analyze_skill_gap.
4. If the goal is interview preparation: start with analyze_candidate_profile -> analyze_skill_gap.

Respond with JSON in this format:
{{
  "intent_analysis": "string",
  "plan": [
    {{
      "step": 1,
      "tool": "tool_name",
      "description": "Clear step description",
      "params": {{}}
    }}
  ]
}}
"""
        llm = get_llm_provider()
        try:
            res = llm.generate_json(prompt, system_instruction)
            plan = res.get("plan", [])
            if isinstance(plan, list) and len(plan) > 0:
                logger.info(f"Gemini successfully generated plan with {len(plan)} steps.")
                return plan
        except Exception as e:
            logger.warning(f"Gemini planning failed: {e}. Falling back to dynamic rule-based plan.")

        # Fallback Dynamic Planner
        return self._fallback_plan(goal, candidate_summary)

    def _fallback_plan(self, goal: str, candidate_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        g_lower = goal.lower()
        plan = []
        step_num = 1

        if "saved" in g_lower:
            plan.append({
                "step": step_num,
                "tool": "retrieve_saved_opportunities",
                "description": "Retrieve candidate's saved internship bookmarks",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "calculate_match",
                "description": "Calculate multi-factor deterministic match scores for saved jobs",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "check_eligibility",
                "description": "Verify eligibility against explicit job requirements",
                "params": {}
            })
        elif "skill gap" in g_lower or "roadmap" in g_lower:
            plan.append({
                "step": step_num,
                "tool": "analyze_candidate_profile",
                "description": "Analyze candidate skills and verified resume data",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "discover_opportunities",
                "description": "Discover domain opportunities for skill benchmarking",
                "params": {"query": goal}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "analyze_skill_gap",
                "description": "Compute prioritized missing skills and learning roadmap",
                "params": {}
            })
        else:
            # Full autonomous discovery and preparation workflow
            domain = None
            if any(k in g_lower for k in ["ai", "ml", "machine learning", "data science"]):
                domain = "AI/ML"
            elif any(k in g_lower for k in ["web", "frontend", "full stack", "react", "node"]):
                domain = "Software Development"
            
            work_mode = "Remote" if "remote" in g_lower else "Any"

            plan.append({
                "step": step_num,
                "tool": "analyze_candidate_profile",
                "description": "Analyze candidate skills, projects, and target preferences",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "discover_opportunities",
                "description": "Discover relevant internships via Hybrid RAG vector search",
                "params": {"query": goal, "domain": domain, "work_mode": work_mode}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "calculate_match",
                "description": "Calculate deterministic compatibility scores and explainable factors",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "check_eligibility",
                "description": "Verify graduation batch and degree eligibility",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "analyze_skill_gap",
                "description": "Analyze skill gaps for top matching roles",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "prepare_application_package",
                "description": "Generate tailored cover letter and resume adaptations (requires approval)",
                "params": {}
            })
            step_num += 1
            plan.append({
                "step": step_num,
                "tool": "track_application",
                "description": "Track top opportunities in application pipeline",
                "params": {"status": "AWAITING_USER_APPROVAL"}
            })

        return plan

    def _emit_event(
        self,
        db: Session,
        run_id: int,
        event_type: str,
        message: str,
        tool_name: Optional[str] = None,
        structured_data: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        event = AgentEvent(
            run_id=run_id,
            event_type=event_type,
            message=message,
            tool_name=tool_name,
            structured_data=structured_data or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def execute_run(self, run_id: int, db: Session) -> AgentRun:
        """
        Executes an AgentRun synchronously step-by-step, recording events to DB.
        """
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not agent_run:
            raise ValueError(f"AgentRun {run_id} not found")

        user_id = agent_run.user_id
        goal = agent_run.goal

        # 1. Start Run
        agent_run.status = "RUNNING"
        db.commit()

        self._emit_event(
            db=db,
            run_id=run_id,
            event_type="agent_run_started",
            message=f"CareerForge agent started execution for goal: '{goal}'"
        )

        # 2. Get initial profile context for planning
        candidate_context = analyze_candidate_profile(user_id=user_id, db=db)
        self._emit_event(
            db=db,
            run_id=run_id,
            event_type="profile_context_loaded",
            message=f"Loaded candidate profile ({len(candidate_context.get('skills', []))} skills, {len(candidate_context.get('projects', []))} projects)",
            tool_name="analyze_candidate_profile",
            structured_data={"skills_count": len(candidate_context.get('skills', [])), "missing_critical": candidate_context.get("missing_critical_info", [])}
        )

        # 3. Create Execution Plan with Gemini
        agent_run.status = "PLANNING"
        db.commit()

        raw_plan = self.plan_with_gemini(goal=goal, candidate_summary=candidate_context)
        
        # Initialize steps status
        plan_steps = []
        for p in raw_plan:
            plan_steps.append({
                "step": p.get("step"),
                "tool": p.get("tool"),
                "description": p.get("description"),
                "params": p.get("params", {}),
                "status": "pending",
                "result_summary": None
            })

        agent_run.execution_plan = plan_steps
        agent_run.status = "RUNNING"
        db.commit()

        self._emit_event(
            db=db,
            run_id=run_id,
            event_type="plan_created",
            message=f"Gemini formulated an autonomous execution plan with {len(plan_steps)} distinct tool operations",
            structured_data={"steps": plan_steps}
        )

        # Intermediate Execution State
        execution_state: Dict[str, Any] = {
            "candidate_context": candidate_context,
            "opportunities": [],
            "matches": [],
            "eligibility_results": {},
            "skill_gaps": {},
            "application_package": None,
            "requires_approval": False
        }

        # 4. Multi-Step Execution Loop
        for idx, step in enumerate(plan_steps):
            tool_name = step.get("tool")
            params = step.get("params", {})
            step["status"] = "running"
            agent_run.execution_plan = list(plan_steps)
            db.commit()

            self._emit_event(
                db=db,
                run_id=run_id,
                event_type="tool_started",
                message=f"Executing Step {step['step']}: {step['description']}",
                tool_name=tool_name
            )

            try:
                if tool_name == "analyze_candidate_profile":
                    candidate_context = analyze_candidate_profile(user_id=user_id, db=db)
                    execution_state["candidate_context"] = candidate_context
                    step["result_summary"] = f"Extracted {len(candidate_context.get('skills', []))} skills, {len(candidate_context.get('educations', []))} degrees."

                elif tool_name == "discover_opportunities":
                    dom = params.get("domain") or (candidate_context.get("profile", {}).get("preferred_domains", ["Software Development"])[0] if candidate_context.get("profile", {}).get("preferred_domains") else None)
                    wm = params.get("work_mode") or candidate_context.get("profile", {}).get("preferred_work_mode", "Any")
                    loc = params.get("location")
                    q = params.get("query")

                    disc_res = discover_opportunities(
                        query=q,
                        domain=dom,
                        location=loc,
                        work_mode=wm,
                        candidate_skills=candidate_context.get("skill_names", []),
                        candidate_preferences=candidate_context.get("profile", {}),
                        limit=8,
                        db=db
                    )
                    execution_state["opportunities"] = disc_res.get("opportunities", [])
                    step["result_summary"] = f"Discovered {len(execution_state['opportunities'])} verified opportunities via Hybrid RAG."
                    
                    self._emit_event(
                        db=db,
                        run_id=run_id,
                        event_type="opportunities_discovered",
                        message=f"Found {len(execution_state['opportunities'])} relevant active internships matching candidate criteria",
                        tool_name="discover_opportunities",
                        structured_data={"count": len(execution_state["opportunities"])}
                    )

                elif tool_name == "retrieve_saved_opportunities":
                    saved_res = retrieve_saved_opportunities(user_id=user_id, db=db)
                    execution_state["opportunities"] = saved_res.get("opportunities", [])
                    step["result_summary"] = f"Retrieved {len(execution_state['opportunities'])} saved internships."

                elif tool_name == "calculate_match":
                    matches = []
                    for opp in execution_state["opportunities"]:
                        m = calculate_match(
                            candidate_profile={
                                "experiences": candidate_context.get("experiences", []),
                                "projects": candidate_context.get("projects", []),
                                "educations": candidate_context.get("educations", []),
                                "preferred_work_mode": candidate_context.get("profile", {}).get("preferred_work_mode", "Any"),
                                "preferred_locations": candidate_context.get("profile", {}).get("preferred_locations", []),
                                "preferred_domains": candidate_context.get("profile", {}).get("preferred_domains", [])
                            },
                            candidate_skills=candidate_context.get("skill_names", []),
                            internship=opp
                        )
                        # Attach opportunity details
                        m["opp_details"] = opp
                        matches.append(m)

                    # Sort by match score descending
                    matches.sort(key=lambda x: x.get("match_score", 0.0), reverse=True)
                    execution_state["matches"] = matches
                    top_score = matches[0].get("match_score", 0.0) if matches else 0.0
                    step["result_summary"] = f"Calculated compatibility for {len(matches)} roles (Top match: {top_score}%)."

                    self._emit_event(
                        db=db,
                        run_id=run_id,
                        event_type="matches_calculated",
                        message=f"Evaluated compatibility for {len(matches)} internships (Highest match: {top_score}%)",
                        tool_name="calculate_match",
                        structured_data={"evaluated_count": len(matches), "top_match_score": top_score}
                    )

                elif tool_name == "check_eligibility":
                    for opp in execution_state["opportunities"]:
                        opp_id = opp.get("id")
                        e = check_eligibility(
                            candidate_profile=candidate_context,
                            candidate_skills=candidate_context.get("skill_names", []),
                            internship=opp
                        )
                        execution_state["eligibility_results"][opp_id] = e

                    eligible_count = sum(1 for e in execution_state["eligibility_results"].values() if e.get("status") == "ELIGIBLE")
                    step["result_summary"] = f"Verified {len(execution_state['eligibility_results'])} roles ({eligible_count} fully eligible)."

                    self._emit_event(
                        db=db,
                        run_id=run_id,
                        event_type="eligibility_checked",
                        message=f"Eligibility check completed: {eligible_count} verified eligible opportunities",
                        tool_name="check_eligibility",
                        structured_data={"eligible_count": eligible_count}
                    )

                elif tool_name == "analyze_skill_gap":
                    # Evaluate top 3 matched opportunities
                    target_opps = [m.get("opp_details") for m in execution_state.get("matches", [])[:3] if m.get("opp_details")]
                    if not target_opps and execution_state["opportunities"]:
                        target_opps = execution_state["opportunities"][:3]

                    for opp in target_opps:
                        opp_id = opp.get("id")
                        sg = analyze_skill_gap(
                            candidate_skills=candidate_context.get("skills", []),
                            internship=opp
                        )
                        execution_state["skill_gaps"][opp_id] = sg

                    step["result_summary"] = f"Analyzed skill gaps for top {len(target_opps)} matching roles."

                    self._emit_event(
                        db=db,
                        run_id=run_id,
                        event_type="skill_gap_analyzed",
                        message=f"Generated skill gap matrices and learning roadmaps for top target opportunities",
                        tool_name="analyze_skill_gap"
                    )

                elif tool_name == "prepare_application_package":
                    # Target the top matching opportunity
                    top_match = execution_state["matches"][0] if execution_state.get("matches") else None
                    target_opp = top_match.get("opp_details") if top_match else (execution_state["opportunities"][0] if execution_state.get("opportunities") else None)

                    if target_opp:
                        app_pkg = prepare_application_package(
                            candidate_profile=candidate_context,
                            candidate_skills=candidate_context.get("skill_names", []),
                            internship=target_opp
                        )
                        execution_state["application_package"] = app_pkg
                        execution_state["requires_approval"] = True
                        step["result_summary"] = f"Prepared tailored cover letter and resume adaptations for {target_opp.get('company')}."

                        self._emit_event(
                            db=db,
                            run_id=run_id,
                            event_type="application_prepared",
                            message=f"Created tailored application package for {target_opp.get('company')} — {target_opp.get('title')}",
                            tool_name="prepare_application_package",
                            structured_data={"target_company": target_opp.get("company")}
                        )

                elif tool_name == "track_application":
                    target_status = params.get("status", "PREPARATION_READY")
                    for m in execution_state.get("matches", [])[:3]:
                        opp_id = m.get("internship_id")
                        if opp_id:
                            track_application(
                                user_id=user_id,
                                internship_id=opp_id,
                                status=target_status,
                                match_score=m.get("match_score", 0.0),
                                notes=f"Identified by CareerForge Agent for goal: {goal[:50]}",
                                db=db
                            )
                    step["result_summary"] = f"Recorded top opportunities in application pipeline as {target_status}."

                step["status"] = "completed"
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                step["status"] = "failed"
                step["result_summary"] = f"Error: {str(e)}"
                self._emit_event(
                    db=db,
                    run_id=run_id,
                    event_type="tool_failed",
                    message=f"Tool {tool_name} encountered an error: {str(e)}",
                    tool_name=tool_name
                )

            agent_run.execution_plan = list(plan_steps)
            db.commit()

        # 5. Build Top Ranked Opportunities Payload
        top_ranked_cards = []
        for m in execution_state.get("matches", [])[:5]:
            opp = m.get("opp_details", {})
            opp_id = m.get("internship_id") or opp.get("id")
            elig = execution_state["eligibility_results"].get(opp_id, {"status": "UNKNOWN"})
            sg = execution_state["skill_gaps"].get(opp_id, {})
            
            top_ranked_cards.append({
                "internship_id": opp_id,
                "company": opp.get("company") or m.get("company", "Company"),
                "title": opp.get("title") or m.get("title", "Internship"),
                "location": opp.get("location") or m.get("location", "Remote"),
                "work_mode": opp.get("work_mode") or m.get("work_mode", "Remote"),
                "stipend": opp.get("stipend", "Competitive"),
                "deadline": opp.get("deadline", "Open"),
                "source": opp.get("source", "Curated"),
                "match_score": m.get("match_score", 0.0),
                "factor_breakdown": m.get("factor_breakdown", {}),
                "eligibility_status": elig.get("status", "UNKNOWN"),
                "eligibility_details": elig.get("verified_requirements", []) + elig.get("discrepancies", []),
                "strengths": m.get("strengths", []),
                "missing_requirements": m.get("missing_skills", []),
                "skill_gap_summary": sg.get("summary", ""),
                "critical_skills": [g.get("skill") for g in sg.get("critical_missing_skills", [])],
                "application_url": opp.get("application_url", "#")
            })

        # 6. Generate High-Impact Synthesis Report with Gemini
        summary_payload = self._synthesize_final_report(
            goal=goal,
            candidate_context=candidate_context,
            top_ranked=top_ranked_cards,
            app_package=execution_state["application_package"],
            requires_approval=execution_state["requires_approval"]
        )

        agent_run.final_summary = summary_payload

        # 7. Determine Final Status (Awaiting Approval vs Completed)
        if execution_state["requires_approval"]:
            agent_run.status = "AWAITING_APPROVAL"
            self._emit_event(
                db=db,
                run_id=run_id,
                event_type="approval_requested",
                message="Application package prepared. Human-in-the-loop approval required before advancing application.",
                structured_data={"target_company": top_ranked_cards[0]["company"] if top_ranked_cards else "Target Role"}
            )
        else:
            agent_run.status = "COMPLETED"
            agent_run.completed_at = datetime.now(timezone.utc)
            self._emit_event(
                db=db,
                run_id=run_id,
                event_type="agent_run_completed",
                message="Autonomous task completed successfully. Final report ready.",
                structured_data={"evaluated_count": len(top_ranked_cards)}
            )

        db.commit()
        db.refresh(agent_run)
        return agent_run

    def _synthesize_final_report(
        self,
        goal: str,
        candidate_context: Dict[str, Any],
        top_ranked: List[Dict[str, Any]],
        app_package: Optional[Dict[str, Any]],
        requires_approval: bool
    ) -> Dict[str, Any]:
        """
        Uses Gemini to generate a factual, concise final report summary with real metrics.
        """
        total_eval = len(top_ranked)
        high_matches = sum(1 for o in top_ranked if o.get("match_score", 0) >= 75)
        eligible_count = sum(1 for o in top_ranked if o.get("eligibility_status") == "ELIGIBLE")

        system_instruction = (
            "You are CareerForge AI synthesizing the results of an autonomous internship workflow. "
            "Never hallucinate numbers or claims. Only use the provided evaluation facts. "
            "Output valid JSON only with 'executive_summary' (string), 'metrics' (object), and 'next_actions' (list of strings)."
        )

        prompt = f"""
User Goal: "{goal}"
Candidate: {candidate_context.get('profile', {}).get('full_name', 'Student')}

Evaluated Opportunities:
{json.dumps([{
    'company': o['company'],
    'title': o['title'],
    'match_score': o['match_score'],
    'eligibility': o['eligibility_status'],
    'strengths': o['strengths'][:2],
    'missing': o['missing_requirements'][:2]
} for o in top_ranked], indent=2)}

Application Package Prepared: {bool(app_package)}
Requires User Approval: {requires_approval}

Respond with JSON:
{{
  "executive_summary": "I analyzed your candidate profile and evaluated ...",
  "metrics": {{
    "total_evaluated": {total_eval},
    "high_confidence_matches": {high_matches},
    "verified_eligible": {eligible_count}
  }},
  "next_actions": [
    "Prioritized actionable step 1",
    "Prioritized actionable step 2"
  ]
}}
"""
        llm = get_llm_provider()
        try:
            res = llm.generate_json(prompt, system_instruction)
            if res and "executive_summary" in res:
                res["top_opportunities"] = top_ranked
                res["application_package"] = app_package
                return res
        except Exception as e:
            logger.warning(f"Error in Gemini final synthesis: {e}")

        # Deterministic fallback summary
        next_actions = []
        if top_ranked:
            next_actions.append(f"Review and apply to top-rated match: {top_ranked[0]['company']} ({top_ranked[0]['match_score']}% match)")
        if app_package:
            next_actions.append(f"Review and approve tailored application package for {top_ranked[0]['company']}")
        if top_ranked and top_ranked[0].get("critical_skills"):
            next_actions.append(f"Close critical skill gaps in: {', '.join(top_ranked[0]['critical_skills'][:2])}")

        return {
            "executive_summary": f"I analyzed your profile against active internships. Found {total_eval} relevant opportunities, with {high_matches} high-confidence matches and {eligible_count} verified as eligible based on available criteria.",
            "metrics": {
                "total_evaluated": total_eval,
                "high_confidence_matches": high_matches,
                "verified_eligible": eligible_count
            },
            "next_actions": next_actions,
            "top_opportunities": top_ranked,
            "application_package": app_package
        }

    def approve_run(self, run_id: int, user_id: int, db: Session, notes: Optional[str] = None) -> AgentRun:
        """
        Human-in-the-Loop Gate: User approves prepared materials and confirms application readiness.
        """
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id, AgentRun.user_id == user_id).first()
        if not agent_run:
            raise ValueError("Agent run not found")

        agent_run.status = "COMPLETED"
        agent_run.completed_at = datetime.now(timezone.utc)

        # Update application state in database to APPLIED / PREPARATION_READY
        top_opp = agent_run.final_summary.get("top_opportunities", [])
        if top_opp:
            target_id = top_opp[0].get("internship_id")
            if target_id:
                track_application(
                    user_id=user_id,
                    internship_id=target_id,
                    status="PREPARATION_READY",
                    match_score=top_opp[0].get("match_score", 0.0),
                    notes=notes or "Approved by student via CareerForge Agent Workspace",
                    db=db
                )

        self._emit_event(
            db=db,
            run_id=run_id,
            event_type="user_approved",
            message="User approved application package. Application status set to PREPARATION_READY.",
            structured_data={"approved_at": datetime.now(timezone.utc).isoformat()}
        )

        db.commit()
        db.refresh(agent_run)
        return agent_run

    def cancel_run(self, run_id: int, user_id: int, db: Session) -> AgentRun:
        """
        Cancels an ongoing or paused run.
        """
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id, AgentRun.user_id == user_id).first()
        if not agent_run:
            raise ValueError("Agent run not found")

        agent_run.status = "CANCELLED"
        agent_run.completed_at = datetime.now(timezone.utc)

        self._emit_event(
            db=db,
            run_id=run_id,
            event_type="agent_run_cancelled",
            message="Agent run was cancelled by user."
        )

        db.commit()
        db.refresh(agent_run)
        return agent_run


orchestrator = AutonomousAgentOrchestrator()
