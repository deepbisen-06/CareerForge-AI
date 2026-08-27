from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.models.entities import User, Internship, InterviewSession, InterviewQuestion
from app.schemas.schemas import (
    GenerateQuestionsRequest, InterviewSessionOut, InterviewQuestionOut,
    SubmitAnswerRequest, PrepPlanOut, InterviewProgressOut
)
from app.auth.deps import get_current_user
from app.agents.interview_agent import interview_agent

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])

@router.post("/generate-questions", response_model=InterviewSessionOut)
def generate_questions(
    req: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == req.internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    prof_dict = {
        "full_name": current_user.profile.full_name if current_user.profile else "Student",
        "projects": [{"title": p.title, "description": p.description} for p in current_user.projects]
    }
    internship_dict = {
        "id": internship.id,
        "company": internship.company,
        "title": internship.title,
        "requirements": internship.requirements or []
    }

    questions_data = interview_agent.generate_question_bank(internship_dict, prof_dict, count=req.count)

    session = InterviewSession(
        user_id=current_user.id,
        internship_id=internship.id,
        role_title=internship.title,
        score=0.0,
        readiness_score=0.0,
        feedback_summary="Session initialized. Submit answers to receive live AI evaluation."
    )
    db.add(session)
    db.flush()

    for q in questions_data:
        db.add(InterviewQuestion(
            session_id=session.id,
            question=q["question"],
            category=q["category"],
            difficulty=q["difficulty"],
            ideal_answer=q["ideal_answer"],
            expected_concepts=q.get("expected_concepts", [])
        ))

    db.commit()
    db.refresh(session)
    return session

@router.get("/prep-plan/{internship_id}", response_model=PrepPlanOut)
def get_preparation_plan(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    prof_dict = {"full_name": current_user.profile.full_name if current_user.profile else "Student"}
    internship_dict = {
        "id": internship.id,
        "company": internship.company,
        "title": internship.title,
        "requirements": internship.requirements or []
    }

    five_day_plan = interview_agent.generate_5_day_plan(internship_dict, prof_dict)
    return PrepPlanOut(
        internship_id=internship.id,
        role_title=internship.title,
        company=internship.company,
        five_day_plan=five_day_plan
    )

@router.post("/submit-answer", response_model=InterviewQuestionOut)
def submit_interview_answer(
    req: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q_obj = db.query(InterviewQuestion).filter(InterviewQuestion.id == req.question_id).first()
    if not q_obj:
        raise HTTPException(status_code=404, detail="Question not found")

    eval_result = interview_agent.evaluate_answer(
        question=q_obj.question,
        ideal_answer=q_obj.ideal_answer or "",
        user_answer=req.user_answer,
        expected_concepts=q_obj.expected_concepts or []
    )

    q_obj.user_answer = req.user_answer
    q_obj.score = eval_result["score"]
    q_obj.feedback = eval_result["feedback"]
    q_obj.detected_concepts = eval_result["detected_concepts"]
    q_obj.missing_concepts = eval_result["missing_concepts"]
    q_obj.evaluation_criteria = eval_result["criteria"]

    # Recalculate session readiness and category scores
    session = q_obj.session
    answered_questions = [q for q in session.questions if q.score is not None]
    if answered_questions:
        avg_score = sum(q.score for q in answered_questions) / len(answered_questions)
        session.score = round(avg_score, 1)
        session.readiness_score = round(avg_score * 10.0, 1)
        
        # Category breakdown
        cat_scores = {}
        for cat in set(q.category for q in answered_questions):
            c_qs = [q for q in answered_questions if q.category == cat]
            cat_scores[cat] = round(sum(q.score for q in c_qs) / len(c_qs), 1)
        session.category_scores = cat_scores
        session.feedback_summary = f"Completed {len(answered_questions)}/{len(session.questions)} questions. Current Readiness: {session.readiness_score}%."

    db.commit()
    db.refresh(q_obj)
    return q_obj

@router.get("/progress", response_model=InterviewProgressOut)
def get_interview_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns multi-session interview progress, readiness trends, and weak topics.
    """
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.asc()).all()

    readiness_trend = []
    category_totals: Dict[str, List[float]] = {}
    recurring_misses: Dict[str, int] = {}

    for idx, s in enumerate(sessions, 1):
        if s.readiness_score > 0:
            readiness_trend.append({
                "session_number": idx,
                "role_title": s.role_title,
                "score": s.readiness_score,
                "date": s.created_at.strftime("%b %d")
            })
        for q in s.questions:
            if q.score is not None:
                category_totals.setdefault(q.category, []).append(q.score)
            for miss in (q.missing_concepts or []):
                recurring_misses[miss] = recurring_misses.get(miss, 0) + 1

    category_averages = {cat: round(sum(scores)/len(scores), 1) for cat, scores in category_totals.items()}
    weak_topics = sorted(recurring_misses.keys(), key=lambda k: recurring_misses[k], reverse=True)[:5]

    overall_avg = round(sum(s.readiness_score for s in sessions)/len(sessions), 1) if sessions else 0.0

    return InterviewProgressOut(
        total_sessions=len(sessions),
        average_score=overall_avg,
        readiness_trend=readiness_trend,
        category_averages=category_averages,
        recurring_weak_topics=weak_topics,
        recent_sessions=sessions[-5:]
    )

@router.get("/session/{id}", response_model=InterviewSessionOut)
def get_session_detail(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.id == id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session
